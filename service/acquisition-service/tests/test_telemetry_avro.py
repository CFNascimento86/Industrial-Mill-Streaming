from __future__ import annotations
from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from fastavro import parse_schema

from acquisition_service.avro_codec import (
    TelemetryAvroCodec,
)
from acquisition_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)


def test_telemetry_schema_is_valid(
    telemetry_schema_path,
):
    codec = TelemetryAvroCodec(
        telemetry_schema_path
    )

    schema = codec.schema

    assert schema["type"] == "record"

    assert schema["name"] == (
        "TelemetryObservation"
    )

    assert schema["namespace"] == (
        "ims.telemetry"
    )

    # Se a construção do codec chegou até aqui,
    # parse_schema() já aceitou o schema.
    parse_schema(schema)


def test_telemetry_observation_avro_round_trip(
    telemetry_schema_path,
):
    codec = TelemetryAvroCodec(
        telemetry_schema_path
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
            6,
            18,
            30,
            1,
            123000,
            tzinfo=timezone.utc,
        ),

        observed_at_source=(
            ObservedAtSource.ACQUISITION
        ),

        ingested_at=datetime(
            2026,
            10,
            6,
            18,
            30,
            1,
            125000,
            tzinfo=timezone.utc,
        ),
    )

    payload = codec.serialize(
        observation
    )

    assert isinstance(
        payload,
        bytes,
    )

    assert len(payload) > 0

    restored = codec.deserialize(
        payload
    )

    assert restored == observation
