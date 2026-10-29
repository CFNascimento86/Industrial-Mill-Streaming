from __future__ import annotations
from uuid import UUID
import pytest

from datetime import (
    datetime,
    timezone,
)

from processing_service.context import (
    FeedLoadCondition,
)

from processing_service.context_processor import (
    OperationalContextProcessor,
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


def observation(
    *,
    telemetry_id: str,
    value: float,
    variable_name: str = "cane_flow",
):
    return TelemetryObservation(
        telemetry_id=UUID(
            telemetry_id
        ),

        variable_id=UUID(
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
        ),

        variable_logical_name=(
            variable_name
        ),

        source_id=UUID(
            "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
        ),

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
            29,
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
            29,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )


class FakePublisher:
    def __init__(
        self,
        *,
        fail: bool = False,
    ):
        self.fail = fail
        self.transitions = []

    def publish(
        self,
        transition,
    ):
        self.transitions.append(
            transition
        )

        if self.fail:
            raise RuntimeError(
                "publication failure"
            )


def build_processor(
    *,
    publisher,
):
    inferer = (
        MillingFeedLoadInferer(
            scope_id=SCOPE_ID
        )
    )

    processor = (
        OperationalContextProcessor(
            inferer=inferer,
            publisher=publisher,
        )
    )

    return (
        inferer,
        processor,
    )


def test_successful_publication_accepts_state():
    publisher = FakePublisher()

    inferer, processor = (
        build_processor(
            publisher=publisher
        )
    )

    transition = processor.process(
        observation(
            telemetry_id=(
                "00000000-0000-4000-8000-000000000001"
            ),
            value=300.0,
        )
    )

    assert transition is not None

    assert len(
        publisher.transitions
    ) == 1

    assert inferer.state == (
        FeedLoadCondition.NORMAL
    )


def test_failed_publication_does_not_accept_state():
    publisher = FakePublisher(
        fail=True
    )

    inferer, processor = (
        build_processor(
            publisher=publisher
        )
    )

    with pytest.raises(
        RuntimeError,
        match="publication failure",
    ):
        processor.process(
            observation(
                telemetry_id=(
                    "00000000-0000-4000-8000-000000000002"
                ),
                value=330.0,
            )
        )

    assert inferer.state is None


def test_failed_change_preserves_previous_state():
    publisher = FakePublisher()

    inferer, processor = (
        build_processor(
            publisher=publisher
        )
    )

    processor.process(
        observation(
            telemetry_id=(
                "00000000-0000-4000-8000-000000000003"
            ),
            value=300.0,
        )
    )

    assert inferer.state == (
        FeedLoadCondition.NORMAL
    )

    publisher.fail = True

    with pytest.raises(
        RuntimeError
    ):
        processor.process(
            observation(
                telemetry_id=(
                    "00000000-0000-4000-8000-000000000004"
                ),
                value=330.0,
            )
        )

    assert inferer.state == (
        FeedLoadCondition.NORMAL
    )


def test_irrelevant_telemetry_produces_nothing():
    publisher = FakePublisher()

    inferer, processor = (
        build_processor(
            publisher=publisher
        )
    )

    result = processor.process(
        observation(
            telemetry_id=(
                "00000000-0000-4000-8000-000000000005"
            ),
            value=80.0,
            variable_name=(
                "main_drive_01_torque"
            ),
        )
    )

    assert result is None

    assert publisher.transitions == []

    assert inferer.state is None
