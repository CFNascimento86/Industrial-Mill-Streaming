from __future__ import annotations
import os
from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

import pytest

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
            "Registry integration test requires "
            "RUN_REGISTRY_INTEGRATION_TESTS=1."
        ),
    ),
]


def test_registered_telemetry_schema_round_trip():
    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        "http://localhost:8080/apis/registry/v3",
    )

    client = ApicurioRegistryClient(
        registry_url,
        timeout=5.0,
    )

    registered = client.resolve_avro_schema(
        group_id="ims.telemetry",
        artifact_id="telemetry-observation",
        version="1.0.0",
    )

    assert registered.group_id == (
        "ims.telemetry"
    )

    assert registered.artifact_id == (
        "telemetry-observation"
    )

    assert registered.version == (
        "1.0.0"
    )

    assert registered.artifact_type == (
        "AVRO"
    )

    assert registered.state in {
        "ENABLED",
        "DEPRECATED",
    }

    assert registered.global_id > 0
    assert registered.content_id > 0

    assert registered.schema["type"] == (
        "record"
    )

    assert registered.schema["name"] == (
        "TelemetryObservation"
    )

    assert registered.schema["namespace"] == (
        "ims.telemetry"
    )

    codec = TelemetryAvroCodec(
        registered.schema
    )

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
            10,
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
            10,
            12,
            0,
            0,
            125000,
            tzinfo=timezone.utc,
        ),
    )

    payload = codec.serialize(
        observation
    )

    restored = codec.deserialize(
        payload
    )

    assert restored == observation
