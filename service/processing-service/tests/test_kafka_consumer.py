from __future__ import annotations
from uuid import UUID
import pytest

from datetime import (
    datetime,
    timezone,
)

from processing_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)

from processing_service.kafka_consumer import (
    KafkaTelemetryConsumer,
)


VARIABLE_ID = UUID(
    "11111111-1111-4111-8111-111111111111"
)


def make_observation():
    return TelemetryObservation(
        telemetry_id=UUID(
            "33333333-3333-4333-8333-333333333333"
        ),

        variable_id=VARIABLE_ID,

        variable_logical_name=(
            "cane_flow"
        ),

        source_id=UUID(
            "22222222-2222-4222-8222-222222222222"
        ),

        source_logical_name=(
            "s7_1500_milling"
        ),

        value=301.42,

        quality=(
            TelemetryQuality.UNKNOWN
        ),

        observed_at=datetime(
            2026,
            10,
            22,
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
            22,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )


class FakeMessage:
    def __init__(
        self,
        observation,
    ):
        self._observation = (
            observation
        )

    def error(self):
        return None

    def key(self):
        return str(
            self._observation.variable_id
        ).encode(
            "utf-8"
        )

    def value(self):
        return b"test"


class FakeKafkaConsumer:
    def __init__(
        self,
        message,
    ):
        self.message = message

        self.commits = []

        self.subscriptions = []

    def subscribe(
        self,
        topics,
    ):
        self.subscriptions = topics

    def poll(
        self,
        timeout,
    ):
        message = self.message

        self.message = None

        return message

    def commit(
        self,
        *,
        message,
        asynchronous,
    ):
        self.commits.append(
            (
                message,
                asynchronous,
            )
        )

    def close(self):
        pass


class FakeDecoder:
    def __init__(
        self,
        observation,
    ):
        self.observation = (
            observation
        )

    def decode(
        self,
        value,
    ):
        return self.observation


def test_commit_occurs_after_successful_processing():
    observation = (
        make_observation()
    )

    fake_consumer = (
        FakeKafkaConsumer(
            FakeMessage(
                observation
            )
        )
    )

    consumer = (
        KafkaTelemetryConsumer(
            bootstrap_servers=(
                "unused:9092"
            ),
            decoder=FakeDecoder(
                observation
            ),
            consumer_factory=(
                lambda config:
                    fake_consumer
            ),
        )
    )

    processed = []

    consumed = consumer.poll_once(
        handler=processed.append
    )

    assert consumed is True

    assert processed == [
        observation
    ]

    assert len(
        fake_consumer.commits
    ) == 1

    _, asynchronous = (
        fake_consumer.commits[0]
    )

    assert asynchronous is False


def test_failed_processing_does_not_commit():
    observation = (
        make_observation()
    )

    fake_consumer = (
        FakeKafkaConsumer(
            FakeMessage(
                observation
            )
        )
    )

    consumer = (
        KafkaTelemetryConsumer(
            bootstrap_servers=(
                "unused:9092"
            ),
            decoder=FakeDecoder(
                observation
            ),
            consumer_factory=(
                lambda config:
                    fake_consumer
            ),
        )
    )

    def failing_handler(
        observation,
    ):
        raise RuntimeError(
            "processing failure"
        )

    with pytest.raises(
        RuntimeError,
        match="processing failure",
    ):
        consumer.poll_once(
            handler=failing_handler
        )

    assert (
        fake_consumer.commits
        == []
    )
