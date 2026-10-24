from __future__ import annotations

from processing_service.context import (
    ContextTransition,
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


class MillingFeedLoadInferer:
    """
    Infere a condição de alimentação
    da moagem a partir de cane_flow.

    A inferência possui estado e histerese.

    Uma saída é produzida somente quando
    existe mudança efetiva de contexto.
    """

    CONTEXT_NAME = (
        "milling_feed_load_condition"
    )

    SOURCE_VARIABLE = (
        "cane_flow"
    )

    def __init__(
        self,
        *,
        low_enter: float = 255.0,
        low_exit: float = 270.0,
        high_enter: float = 325.0,
        high_exit: float = 315.0,
        initial_state: (
            FeedLoadCondition
        ) = FeedLoadCondition.NORMAL,
    ) -> None:

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

        self._low_enter = low_enter
        self._low_exit = low_exit

        self._high_enter = high_enter
        self._high_exit = high_exit

        self._state = initial_state

    @property
    def state(
        self,
    ) -> FeedLoadCondition:
        return self._state

    def process(
        self,
        observation: (
            TelemetryObservation
        ),
    ) -> ContextTransition | None:
        """
        Processa uma observação.
        Retorna ContextTransition somente
        quando a condição operacional muda.
        """

        if (
            observation
            .variable_logical_name
            != self.SOURCE_VARIABLE
        ):
            return None

        # BAD representa evidência
        # inadequada para inferência.
        #
        # UNKNOWN é aceito no M1 porque
        # Modbus não fornece qualidade
        # industrial nativa e a aquisição
        # bem-sucedida ainda produz
        # quality=UNKNOWN.
        if (
            observation.quality
            == TelemetryQuality.BAD
        ):
            return None

        previous = self._state

        current = (
            self._evaluate(
                observation.value
            )
        )

        if current == previous:
            return None

        self._state = current

        return ContextTransition(
            context_name=(
                self.CONTEXT_NAME
            ),

            previous_state=previous,
            current_state=current,

            effective_at=(
                observation.observed_at
            ),

            evidence_telemetry_id=(
                observation.telemetry_id
            ),

            evidence_variable_id=(
                observation.variable_id
            ),

            evidence_variable_logical_name=(
                observation
                .variable_logical_name
            ),

            evidence_value=(
                observation.value
            ),
        )

    def _evaluate(
        self,
        value: float,
    ) -> FeedLoadCondition:

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
