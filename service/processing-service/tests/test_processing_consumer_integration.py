from __future__ import annotations
import os
import time
from uuid import uuid4
import pytest

from processing_service.kafka_consumer import (
    KafkaTelemetryConsumer,
)

from processing_service.registry_client import (
    ApicurioRegistryClient,
)

from processing_service.telemetry_decoder import (
    TelemetryMessageDecoder,
)


RUN_INTEGRATION_TESTS = (
    os.getenv(
        "RUN_PROCESSING_CONSUMER_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_INTEGRATION_TESTS,
        reason=(
            "Processing consumer integration "
            "test is disabled."
        ),
    ),
]


def test_processing_consumer_reads_real_telemetry():
    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        "http://localhost:8080/apis/registry/v3",
    )

    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )

    topic = os.getenv(
        "KAFKA_TELEMETRY_TOPIC",
        "ims.telemetry.observation",
    )

    registry = (
        ApicurioRegistryClient(
            registry_url
        )
    )

    decoder = (
        TelemetryMessageDecoder(
            registry_client=registry
        )
    )

    consumer = (
        KafkaTelemetryConsumer(
            bootstrap_servers=(
                bootstrap_servers
            ),
            topic=topic,

            group_id=(
                "ims-processing-test-"
                f"{uuid4()}"
            ),

            # Consumir somente eventos
            # produzidos após o grupo
            # entrar no Kafka.
            auto_offset_reset=(
                "latest"
            ),

            decoder=decoder,
        )
    )

    received = []

    try:
        deadline = (
            time.monotonic()
            + 15.0
        )

        while (
            not received
            and time.monotonic()
            < deadline
        ):
            consumer.poll_once(
                handler=(
                    received.append
                ),
                timeout=1.0,
            )

    finally:
        consumer.close()

    assert len(received) == 1

    observation = (
        received[0]
    )

    assert (
        observation
        .variable_logical_name
    )

    assert (
        observation
        .source_logical_name
        == "s7_1500_milling"
    )

    assert (
        observation
        .observed_at
        .tzinfo
        is not None
    )
