from __future__ import annotations
from uuid import UUID

from datetime import (
    datetime,
    timezone,
)

from processing_service.context import (
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


VARIABLE_ID = UUID(
    "11111111-1111-4111-8111-111111111111"
)

SOURCE_ID = UUID(
    "22222222-2222-4222-8222-222222222222"
)


def observation(
    *,
    telemetry_id: UUID,
    value: float,
    variable_name: str = "cane_flow",
):
    return TelemetryObservation(
        telemetry_id=telemetry_id,
        variable_id=VARIABLE_ID,
        variable_logical_name=(
            variable_name
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
            24,
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
            24,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )


def test_normal_does_not_create_transition():
    inferer = (
        MillingFeedLoadInferer()
    )

    result = inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000001"
            ),
            value=300.0,
        )
    )

    assert result is None

    assert inferer.state == (
        FeedLoadCondition.NORMAL
    )


def test_normal_transitions_to_high():
    inferer = (
        MillingFeedLoadInferer()
    )

    result = inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000002"
            ),
            value=330.0,
        )
    )

    assert result is not None

    assert result.previous_state == (
        FeedLoadCondition.NORMAL
    )

    assert result.current_state == (
        FeedLoadCondition.HIGH
    )

    assert inferer.state == (
        FeedLoadCondition.HIGH
    )


def test_high_hysteresis_prevents_chattering():
    inferer = (
        MillingFeedLoadInferer()
    )

    inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000003"
            ),
            value=330.0,
        )
    )

    # Cai abaixo do enter threshold,
    # mas ainda não ultrapassou o
    # exit threshold.
    result = inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000004"
            ),
            value=320.0,
        )
    )

    assert result is None

    assert inferer.state == (
        FeedLoadCondition.HIGH
    )


def test_high_returns_to_normal():
    inferer = (
        MillingFeedLoadInferer()
    )

    inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000005"
            ),
            value=330.0,
        )
    )

    result = inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000006"
            ),
            value=310.0,
        )
    )

    assert result is not None

    assert result.previous_state == (
        FeedLoadCondition.HIGH
    )

    assert result.current_state == (
        FeedLoadCondition.NORMAL
    )


def test_normal_transitions_to_low():
    inferer = (
        MillingFeedLoadInferer()
    )

    result = inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000007"
            ),
            value=240.0,
        )
    )

    assert result is not None

    assert result.current_state == (
        FeedLoadCondition.LOW
    )


def test_non_cane_flow_is_ignored():
    inferer = (
        MillingFeedLoadInferer()
    )

    result = inferer.process(
        observation(
            telemetry_id=UUID(
                "00000000-0000-4000-8000-000000000008"
            ),
            variable_name=(
                "main_drive_01_torque"
            ),
            value=80.0,
        )
    )

    assert result is None

    assert inferer.state == (
        FeedLoadCondition.NORMAL
    )
