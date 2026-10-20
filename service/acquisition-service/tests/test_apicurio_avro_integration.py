from __future__ import annotations
import pytest
import os

from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from acquisition_service.apicurio_wire import (
    ApicurioWireFramer,
    HEADER_SIZE,
)
from acquisition_service.avro_codec import (
    TelemetryAvroCodec,
)
from acquisition_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)
from acquisition_service.registry_client import (
    ApicurioRegistryClient,
)


RUN_REGISTRY_INTEGRATION_TESTS = (
    os.getenv(
        "RUN_REGISTRY_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_REGISTRY_INTEGRATION_TESTS,
        reason=(
            "Apicurio integration test requires "
            "RUN_REGISTRY_INTEGRATION_TESTS=1."
        ),
    ),
]


def test_registered_schema_produces_kafka_ready_payload():
    # ---------------------------------------------------------
    # Registry configuration
    # ---------------------------------------------------------

    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        "http://localhost:8080/apis/registry/v3",
    )

    registry_client = (
        ApicurioRegistryClient(
            registry_url,
            timeout=5.0,
        )
    )

    # ---------------------------------------------------------
    # Resolve real governed contract
    # ---------------------------------------------------------

    registered = (
        registry_client
        .resolve_avro_schema(
            group_id="ims.telemetry",
            artifact_id=(
                "telemetry-observation"
            ),
            version="1.0.0",
        )
    )

    assert registered.content_id > 0

    assert registered.artifact_type == (
        "AVRO"
    )

    assert registered.state in {
        "ENABLED",
        "DEPRECATED",
    }

    # ---------------------------------------------------------
    # Build runtime serialization components
    # ---------------------------------------------------------

    codec = TelemetryAvroCodec(
        registered.schema
    )

    framer = ApicurioWireFramer(
        content_id=(
            registered.content_id
        )
    )

    # ---------------------------------------------------------
    # Contracted industrial observation
    # ---------------------------------------------------------

    observation = TelemetryObservation(
        telemetry_id=UUID(
            "33333333-3333-4333-8333-333333333333"
        ),

        variable_id=UUID(
            "11111111-1111-4111-8111-111111111111"
        ),

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
            20,
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
            20,
            12,
            0,
            0,
            125000,
            tzinfo=timezone.utc,
        ),
    )

    # ---------------------------------------------------------
    # Avro serialization
    # ---------------------------------------------------------

    avro_payload = codec.serialize(
        observation
    )

    assert isinstance(
        avro_payload,
        bytes,
    )

    assert len(avro_payload) > 0

    # ---------------------------------------------------------
    # Apicurio wire framing
    # ---------------------------------------------------------

    kafka_value = framer.frame(
        avro_payload
    )

    assert isinstance(
        kafka_value,
        bytes,
    )

    assert len(kafka_value) == (
        HEADER_SIZE
        + len(avro_payload)
    )

    # Magic byte
    assert kafka_value[0] == 0

    # ---------------------------------------------------------
    # Simulate consumer-side framing resolution
    # ---------------------------------------------------------

    parsed = (
        ApicurioWireFramer.parse(
            kafka_value
        )
    )

    assert parsed.content_id == (
        registered.content_id
    )

    assert parsed.payload == (
        avro_payload
    )

    # ---------------------------------------------------------
    # Avro consumer-side deserialization
    # ---------------------------------------------------------

    restored = codec.deserialize(
        parsed.payload
    )

    assert restored == observation
