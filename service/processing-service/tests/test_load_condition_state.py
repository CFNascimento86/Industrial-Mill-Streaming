from __future__ import annotations
from uuid import UUID

from datetime import (
    datetime,
    timezone,
)

from processing_service.context import (
    ContextTransitionType,
    FeedLoadCondition,
)

from processing_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)

from processing_service.load_condition import (
    MillingFeedLoadInferer,
)


SCOPE_ID = UUID(
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
)

VARIABLE_ID = UUID(
    "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
)

SOURCE_ID = UUID(
    "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
)


def make_observation(
    *,
    telemetry_id: str,
    value: float,
):
    return TelemetryObservation(
        telemetry_id=UUID(
            telemetry_id
        ),

        variable_id=VARIABLE_ID,

        variable_logical_name=(
            "cane_flow"
        ),

        source_id=SOURCE_ID,

        source_logical_name=(
            "s7_1500_milling"
        ),

        value=value,

        quality=(
            TelemetryQuality.UNKNOWN
        ),

        observed_at=datetime(
            2026,
            10,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        ),

        observed_at_source=(
            ObservedAtSource.ACQUISITION
        ),

        ingested_at=datetime(
            2026,
            10,
            26,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )


def build_inferer():
    return MillingFeedLoadInferer(
        scope_id=SCOPE_ID,
    )


def test_first_observation_establishes_state():
    inferer = build_inferer()

    transition = inferer.infer(
        make_observation(
            telemetry_id=(
                "00000000-0000-4000-8000-000000000001"
            ),
            value=300.0,
        )
    )

    assert transition is not None

    assert (
        transition.transition_type
        == ContextTransitionType
        .ESTABLISHED
    )

    assert (
        transition.previous_state
        is None
    )

    assert (
        transition.current_state
        == FeedLoadCondition.NORMAL
    )

    # infer() não confirma estado.
    assert inferer.state is None


def test_accept_confirms_state():
    inferer = build_inferer()

    transition = inferer.infer(
        make_observation(
            telemetry_id=(
                "00000000-0000-4000-8000-000000000002"
            ),
            value=300.0,
        )
    )

    inferer.accept(
        transition
    )

    assert inferer.state == (
        FeedLoadCondition.NORMAL
    )


def test_change_is_not_accepted_implicitly():
    inferer = build_inferer()

    established = inferer.infer(
        make_observation(
            telemetry_id=(
                "00000000-0000-4000-8000-000000000003"
            ),
            value=300.0,
        )
    )

    inferer.accept(
        established
    )

    changed = inferer.infer(
        make_observation(
            telemetry_id=(
                "00000000-0000-4000-8000-000000000004"
            ),
            value=330.0,
        )
    )

    assert changed is not None

    assert (
        changed.transition_type
        == ContextTransitionType
        .CHANGED
    )

    assert (
        changed.previous_state
        == "NORMAL"
    )

    assert (
        changed.current_state
        == "HIGH"
    )

    # Ainda NORMAL até delivery confirmado.
    assert inferer.state == (
        FeedLoadCondition.NORMAL
    )


def test_transition_identity_is_deterministic():
    observation = make_observation(
        telemetry_id=(
            "00000000-0000-4000-8000-000000000005"
        ),
        value=330.0,
    )

    first = (
        build_inferer()
        .infer(
            observation
        )
    )

    second = (
        build_inferer()
        .infer(
            observation
        )
    )

    assert (
        first.context_transition_id
        ==
        second.context_transition_id
    )
