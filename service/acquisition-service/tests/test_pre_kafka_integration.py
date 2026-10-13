from __future__ import annotations
import os
from datetime import timedelta
import pytest
from acquisition_service.avro_codec import (
    TelemetryAvroCodec,
)
from acquisition_service.client import (
    ModbusAcquisitionClient,
)
from acquisition_service.contract import (
    ObservedAtSource,
    TelemetryQuality,
)
from acquisition_service.mapping import (
    build_read_windows,
    build_variable_mappings,
)
from acquisition_service.postgres_identity import (
    PostgresIdentityResolver,
)
from acquisition_service.registry_client import (
    ApicurioRegistryClient,
)
from acquisition_service.runtime import (
    acquire_cycle,
)
from acquisition_service.transformer import (
    TelemetryTransformer,
)


RUN_PRE_KAFKA_TESTS = (
    os.getenv(
        "RUN_PRE_KAFKA_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_PRE_KAFKA_TESTS,
        reason=(
            "Pre-Kafka integration test requires "
            "RUN_PRE_KAFKA_INTEGRATION_TESTS=1."
        ),
    ),
]


EXPECTED_VARIABLE_COUNT = 19


def test_complete_pipeline_before_kafka(
    modbus_mapping_config,
):
    # ---------------------------------------------------------
    # Runtime configuration
    # ---------------------------------------------------------

    database_url = os.environ[
        "DATABASE_URL"
    ]

    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        "http://localhost:8080/apis/registry/v3",
    )

    modbus_host = os.getenv(
        "MODBUS_HOST",
        "127.0.0.1",
    )

    modbus_port = int(
        os.getenv(
            "MODBUS_PORT",
            "1502",
        )
    )

    modbus_device_id = int(
        os.getenv(
            "MODBUS_DEVICE_ID",
            "1",
        )
    )

    source_logical_name = (
        modbus_mapping_config[
            "source"
        ]["logical_name"]
    )

    encoding = (
        modbus_mapping_config[
            "encoding"
        ]["float32"]
    )

    # ---------------------------------------------------------
    # Acquisition model
    # ---------------------------------------------------------

    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    assert len(mappings) == (
        EXPECTED_VARIABLE_COUNT
    )

    assert len(windows) == 5

    expected_names = {
        mapping.logical_name
        for mapping in mappings
    }

    # ---------------------------------------------------------
    # Industrial identity
    # ---------------------------------------------------------

    identity_resolver = (
        PostgresIdentityResolver
        .from_database(
            database_url=database_url,
            source_logical_name=(
                source_logical_name
            ),
        )
    )

    # Valida explicitamente 19/19 identidades
    resolved_identities = [
        identity_resolver.resolve(
            variable_logical_name=(
                mapping.logical_name
            ),
            source_logical_name=(
                source_logical_name
            ),
        )
        for mapping in mappings
    ]

    assert len(
        resolved_identities
    ) == EXPECTED_VARIABLE_COUNT

    variable_ids = {
        identity.variable_id
        for identity in resolved_identities
    }

    source_ids = {
        identity.source_id
        for identity in resolved_identities
    }

    assert len(variable_ids) == (
        EXPECTED_VARIABLE_COUNT
    )

    assert len(source_ids) == 1

    # ---------------------------------------------------------
    # Registry-backed Avro contract
    # ---------------------------------------------------------

    registry_client = (
        ApicurioRegistryClient(
            registry_url,
            timeout=5.0,
        )
    )

    registered_schema = (
        registry_client
        .resolve_avro_schema(
            group_id="ims.telemetry",
            artifact_id=(
                "telemetry-observation"
            ),
            version="1.0.0",
        )
    )

    codec = TelemetryAvroCodec(
        registered_schema.schema
    )

    # ---------------------------------------------------------
    # Telemetry transformation
    # ---------------------------------------------------------

    transformer = TelemetryTransformer(
        identity_resolver=(
            identity_resolver
        ),
        source_logical_name=(
            source_logical_name
        ),
    )

    # ---------------------------------------------------------
    # Real Modbus acquisition
    # ---------------------------------------------------------

    client = ModbusAcquisitionClient(
        host=modbus_host,
        port=modbus_port,
        device_id=modbus_device_id,
        byte_order=encoding[
            "byte_order"
        ],
        word_order=encoding[
            "word_order"
        ],
        timeout=3.0,
    )

    try:
        client.connect()

        readings = acquire_cycle(
            client=client,
            windows=windows,
        )

    finally:
        client.close()

    assert len(readings) == (
        EXPECTED_VARIABLE_COUNT
    )

    assert {
        reading.logical_name
        for reading in readings
    } == expected_names

    # ---------------------------------------------------------
    # AcquisitionReading -> TelemetryObservation
    # ---------------------------------------------------------

    observations = tuple(
        transformer.transform(
            reading
        )
        for reading in readings
    )

    assert len(observations) == (
        EXPECTED_VARIABLE_COUNT
    )

    assert {
        observation.variable_logical_name
        for observation in observations
    } == expected_names

    # Uma observação = uma identidade própria.
    telemetry_ids = {
        observation.telemetry_id
        for observation in observations
    }

    assert len(telemetry_ids) == (
        EXPECTED_VARIABLE_COUNT
    )

    # Uma identidade estável por variável.
    observation_variable_ids = {
        observation.variable_id
        for observation in observations
    }

    assert observation_variable_ids == (
        variable_ids
    )

    # Todas pertencem à mesma fonte industrial.
    observation_source_ids = {
        observation.source_id
        for observation in observations
    }

    assert observation_source_ids == (
        source_ids
    )

    assert all(
        observation.source_logical_name
        == source_logical_name
        for observation in observations
    )

    # Modbus M1 não fornece timestamp industrial.
    assert all(
        observation.observed_at_source
        == ObservedAtSource.ACQUISITION
        for observation in observations
    )

    # Sucesso de comunicação != qualidade GOOD.
    assert all(
        observation.quality
        == TelemetryQuality.UNKNOWN
        for observation in observations
    )

    # Temporalidade explícita em UTC.
    assert all(
        observation.observed_at.tzinfo
        is not None
        and
        observation.observed_at.utcoffset()
        == timedelta(0)
        for observation in observations
    )

    assert all(
        observation.ingested_at.tzinfo
        is not None
        and
        observation.ingested_at.utcoffset()
        == timedelta(0)
        for observation in observations
    )

    # ---------------------------------------------------------
    # Avro serialization
    # ---------------------------------------------------------

    payloads = tuple(
        codec.serialize(
            observation
        )
        for observation in observations
    )

    assert len(payloads) == (
        EXPECTED_VARIABLE_COUNT
    )

    assert all(
        isinstance(payload, bytes)
        and len(payload) > 0
        for payload in payloads
    )

    # ---------------------------------------------------------
    # Round-trip contract validation
    # ---------------------------------------------------------

    restored = tuple(
        codec.deserialize(
            payload
        )
        for payload in payloads
    )

    assert restored == observations
