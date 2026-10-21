from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from acquisition_service.apicurio_wire import (
    ApicurioWireFramer,
)
from acquisition_service.avro_codec import (
    TelemetryAvroCodec,
)
from acquisition_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)
from acquisition_service.kafka_producer import (
    KafkaDeliveryError,
    KafkaDeliveryPendingError,
)
from acquisition_service.telemetry_publisher import (
    TelemetryPublisher,
)


VARIABLE_ID = UUID(
    "11111111-1111-4111-8111-111111111111"
)

SOURCE_ID = UUID(
    "22222222-2222-4222-8222-222222222222"
)

TELEMETRY_ID = UUID(
    "33333333-3333-4333-8333-333333333333"
)


class FakeTransport:
    def __init__(
        self,
        *,
        flush_results,
    ):
        self.published = []
        self.flush_results = list(
            flush_results
        )
        self.flush_count = 0

    def publish(
        self,
        *,
        variable_id,
        value,
    ):
        self.published.append(
            (
                variable_id,
                value,
            )
        )

    def flush(
        self,
        *,
        timeout=10.0,
    ):
        self.flush_count += 1

        if not self.flush_results:
            return

        result = (
            self.flush_results.pop(0)
        )

        if isinstance(
            result,
            Exception,
        ):
            raise result


def make_observation():
    return TelemetryObservation(
        telemetry_id=(
            TELEMETRY_ID
        ),

        variable_id=(
            VARIABLE_ID
        ),

        variable_logical_name=(
            "cane_flow"
        ),

        source_id=(
            SOURCE_ID
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
            21,
            12,
            0,
            0,
            123000,
            tzinfo=timezone.utc,
        ),

        observed_at_source=(
            ObservedAtSource.ACQUISITION
        ),

        ingested_at=datetime(
            2026,
            10,
            21,
            12,
            0,
            0,
            125000,
            tzinfo=timezone.utc,
        ),
    )


def test_delivery_timeout_does_not_republish(
    telemetry_schema_path,
):
    transport = FakeTransport(
        flush_results=[
            KafkaDeliveryPendingError(
                "still pending"
            ),
            KafkaDeliveryPendingError(
                "still pending"
            ),
            None,
        ]
    )

    publisher = TelemetryPublisher(
        codec=(
            TelemetryAvroCodec.from_path(
                telemetry_schema_path
            )
        ),
        framer=(
            ApicurioWireFramer(
                content_id=17
            )
        ),
        transport=transport,
        sleeper=lambda _: None,
    )

    observation = make_observation()

    count = publisher.publish_batch(
        [observation]
    )

    assert count == 1

    # Uma única publicação.
    assert len(
        transport.published
    ) == 1

    # Porém três esperas de delivery.
    assert transport.flush_count == 3


def test_final_delivery_failure_republishes_same_payload(
    telemetry_schema_path,
):
    transport = FakeTransport(
        flush_results=[
            KafkaDeliveryError(
                "broker delivery failure"
            ),
            None,
        ]
    )

    publisher = TelemetryPublisher(
        codec=(
            TelemetryAvroCodec.from_path(
                telemetry_schema_path
            )
        ),
        framer=(
            ApicurioWireFramer(
                content_id=17
            )
        ),
        transport=transport,
        max_attempts=2,
        retry_backoff_seconds=0,
        sleeper=lambda _: None,
    )

    observation = make_observation()

    count = publisher.publish_batch(
        [observation]
    )

    assert count == 1

    # Houve republicação após
    # falha definitiva.
    assert len(
        transport.published
    ) == 2

    first_variable_id, first_value = (
        transport.published[0]
    )

    second_variable_id, second_value = (
        transport.published[1]
    )

    assert first_variable_id == (
        VARIABLE_ID
    )

    assert second_variable_id == (
        VARIABLE_ID
    )

    # O ponto central:
    # exatamente os mesmos bytes.
    assert second_value == first_value

    framer_result = (
        ApicurioWireFramer.parse(
            second_value
        )
    )

    codec = (
        TelemetryAvroCodec.from_path(
            telemetry_schema_path
        )
    )

    restored = codec.deserialize(
        framer_result.payload
    )

    # O telemetry_id original continua
    # exatamente o mesmo.
    assert restored.telemetry_id == (
        TELEMETRY_ID
    )

    assert restored == observation
  
