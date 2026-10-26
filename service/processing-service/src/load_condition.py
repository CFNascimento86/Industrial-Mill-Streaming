from __future__ import annotations
from collections.abc import Callable
from datetime import (
    datetime,
    timezone,
)

from uuid import (
    NAMESPACE_URL,
    UUID,
    uuid5,
)

from processing_service.context import (
    ContextOrigin,
    ContextScopeType,
    ContextTransition,
    ContextTransitionType,
    FeedLoadCondition,
)
from processing_service.contract import (
    TelemetryObservation,
    TelemetryQuality,
)


class LoadConditionInferenceError(
    ValueError
):
    pass


CONTEXT_TRANSITION_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:ims:context-transition",
)


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def _millisecond_precision(
    value: datetime,
) -> datetime:
    return value.replace(
        microsecond=(
            value.microsecond
            // 1000
        )
        * 1000
    )


class MillingFeedLoadInferer:
    """
    Infere a condição de alimentação
    da moagem através de cane_flow.

    Importante:

    infer()
        não modifica estado.

    accept()
        confirma a mudança somente após
        a publicação downstream ter sido
        concluída.
    """

    CONTEXT_LOGICAL_NAME = (
        "milling_feed_load_condition"
    )

    SOURCE_VARIABLE = (
        "cane_flow"
    )

    RULE_ID = (
        "milling_feed_load_condition"
    )

    RULE_VERSION = "1.0"

    def __init__(
        self,
        *,
        scope_id: UUID,
        scope_logical_name: str = "milling",
        low_enter: float = 255.0,
        low_exit: float = 270.0,
        high_enter: float = 325.0,
        high_exit: float = 315.0,
        clock: Callable[
            [],
            datetime,
        ] = utc_now,
    ) -> None:

        if not isinstance(
            scope_id,
            UUID,
        ):
            raise (
                LoadConditionInferenceError(
                    "scope_id must be UUID."
                )
            )

        if not (
            scope_logical_name.strip()
        ):
            raise (
                LoadConditionInferenceError(
                    "scope_logical_name "
                    "cannot be empty."
                )
            )

        if not (
            low_enter
            < low_exit
            < high_exit
            < high_enter
        ):
            raise (
                LoadConditionInferenceError(
                    "Invalid hysteresis "
                    "threshold configuration."
                )
            )

        self._scope_id = scope_id

        self._scope_logical_name = (
            scope_logical_name
        )

        self._low_enter = low_enter
        self._low_exit = low_exit

        self._high_enter = high_enter
        self._high_exit = high_exit

        self._clock = clock

        # Nenhum estado é presumido
        # durante startup.
        self._state: (
            FeedLoadCondition
            | None
        ) = None

    @property
    def state(
        self,
    ) -> FeedLoadCondition | None:
        return self._state

    def infer(
        self,
        observation: (
            TelemetryObservation
        ),
    ) -> ContextTransition | None:
        """
        Avalia uma observação sem modificar
        o estado confirmado do inferer.
        """

        if (
            observation
            .variable_logical_name
            != self.SOURCE_VARIABLE
        ):
            return None

        if (
            observation.quality
            == TelemetryQuality.BAD
        ):
            return None

        previous = self._state

        if previous is None:
            current = (
                self._classify_initial(
                    observation.value
                )
            )

            transition_type = (
                ContextTransitionType
                .ESTABLISHED
            )

            previous_state = None

        else:
            current = self._evaluate(
                observation.value
            )

            if current == previous:
                return None

            transition_type = (
                ContextTransitionType
                .CHANGED
            )

            previous_state = (
                previous.value
            )

        transition_id = (
            self._build_transition_id(
                observation=observation
            )
        )

        produced_at = (
            _millisecond_precision(
                self._clock()
            )
        )

        return ContextTransition(
            context_transition_id=(
                transition_id
            ),

            context_logical_name=(
                self.CONTEXT_LOGICAL_NAME
            ),

            transition_type=(
                transition_type
            ),

            previous_state=(
                previous_state
            ),

            current_state=(
                current.value
            ),

            scope_type=(
                ContextScopeType.PROCESS
            ),

            scope_id=(
                self._scope_id
            ),

            scope_logical_name=(
                self._scope_logical_name
            ),

            effective_at=(
                _millisecond_precision(
                    observation.observed_at
                )
            ),

            produced_at=produced_at,

            origin=(
                ContextOrigin.INFERRED
            ),

            evidence_telemetry_ids=(
                observation.telemetry_id,
            ),

            inference_rule_id=(
                self.RULE_ID
            ),

            inference_rule_version=(
                self.RULE_VERSION
            ),
        )

    def accept(
        self,
        transition: ContextTransition,
    ) -> None:
        """
        Confirma uma transição somente após
        seu efeito downstream ter sido
        concluído.
        """

        if (
            transition
            .context_logical_name
            != self.CONTEXT_LOGICAL_NAME
        ):
            raise (
                LoadConditionInferenceError(
                    "Transition belongs to "
                    "another context."
                )
            )

        if (
            transition.scope_id
            != self._scope_id
        ):
            raise (
                LoadConditionInferenceError(
                    "Transition belongs to "
                    "another scope."
                )
            )

        current = (
            FeedLoadCondition(
                transition.current_state
            )
        )

        if self._state is None:
            if (
                transition.transition_type
                != ContextTransitionType
                .ESTABLISHED
            ):
                raise (
                    LoadConditionInferenceError(
                        "First accepted transition "
                        "must be ESTABLISHED."
                    )
                )

            if (
                transition.previous_state
                is not None
            ):
                raise (
                    LoadConditionInferenceError(
                        "ESTABLISHED transition "
                        "cannot have "
                        "previous_state."
                    )
                )

        else:
            if (
                transition.transition_type
                != ContextTransitionType
                .CHANGED
            ):
                raise (
                    LoadConditionInferenceError(
                        "Existing context requires "
                        "CHANGED transition."
                    )
                )

            if (
                transition.previous_state
                != self._state.value
            ):
                raise (
                    LoadConditionInferenceError(
                        "Transition previous state "
                        "does not match confirmed "
                        "inferer state."
                    )
                )

        self._state = current

    def _classify_initial(
        self,
        value: float,
    ) -> FeedLoadCondition:

        if value <= self._low_enter:
            return FeedLoadCondition.LOW

        if value >= self._high_enter:
            return FeedLoadCondition.HIGH

        return FeedLoadCondition.NORMAL

    def _evaluate(
        self,
        value: float,
    ) -> FeedLoadCondition:

        if self._state is None:
            raise (
                LoadConditionInferenceError(
                    "Cannot evaluate hysteresis "
                    "without confirmed state."
                )
            )

        if (
            self._state
            == FeedLoadCondition.NORMAL
        ):
            if value <= self._low_enter:
                return (
                    FeedLoadCondition.LOW
                )

            if value >= self._high_enter:
                return (
                    FeedLoadCondition.HIGH
                )

            return self._state

        if (
            self._state
            == FeedLoadCondition.LOW
        ):
            if value >= self._low_exit:
                return (
                    FeedLoadCondition.NORMAL
                )

            return self._state

        if (
            self._state
            == FeedLoadCondition.HIGH
        ):
            if value <= self._high_exit:
                return (
                    FeedLoadCondition.NORMAL
                )

            return self._state

        raise (
            LoadConditionInferenceError(
                "Unsupported load state."
            )
        )

    def _build_transition_id(
        self,
        *,
        observation: (
            TelemetryObservation
        ),
    ) -> UUID:
        """
        A mesma evidência reprocessada pela
        mesma regra produz a mesma identidade.
        Isso é essencial para idempotência.
        """

        identity_material = (
            f"{self.CONTEXT_LOGICAL_NAME}:"
            f"{self.RULE_VERSION}:"
            f"{self._scope_id}:"
            f"{observation.telemetry_id}"
        )

        return uuid5(
            CONTEXT_TRANSITION_NAMESPACE,
            identity_material,
        )
