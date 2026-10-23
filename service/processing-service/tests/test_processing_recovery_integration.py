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


RUN_RECOVERY_TESTS = (
    os.getenv(
        "RUN_PROCESSING_RECOVERY_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_RECOVERY_TESTS,
        reason=(
            "Processing recovery integration "
            "test is disabled."
        ),
    ),
]


TARGET_VARIABLE = "cane_flow"


class ExpectedProcessingFailure(
    RuntimeError
):
    pass


def build_consumer(
    *,
    group_id: str,
    bootstrap_servers: str,
    topic: str,
    registry_url: str,
) -> KafkaTelemetryConsumer:
    registry = (
        ApicurioRegistryClient(
            registry_url,
            timeout=5.0,
        )
    )

    decoder = (
        TelemetryMessageDecoder(
            registry_client=registry
        )
    )

    return KafkaTelemetryConsumer(
        bootstrap_servers=(
            bootstrap_servers
        ),
        topic=topic,
        group_id=group_id,

        # O teste precisa apenas de eventos
        # produzidos após sua inicialização.
        auto_offset_reset="latest",

        decoder=decoder,
    )


def test_failed_event_is_redelivered_after_consumer_restart():
    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )

    topic = os.getenv(
        "KAFKA_TELEMETRY_TOPIC",
        "ims.telemetry.observation",
    )

    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        "http://localhost:8080/apis/registry/v3",
    )

    group_id = (
        "ims-processing-recovery-test-"
        f"{uuid4()}"
    )

    # ---------------------------------------------------------
    # First consumer lifecycle
    # ---------------------------------------------------------

    consumer = build_consumer(
        group_id=group_id,
        bootstrap_servers=(
            bootstrap_servers
        ),
        topic=topic,
        registry_url=registry_url,
    )

    target_seen = 0
    first_committed_observation = None
    failed_observation = None

    def failing_handler(
        observation,
    ):
        nonlocal target_seen
        nonlocal first_committed_observation
        nonlocal failed_observation

        if (
            observation.variable_logical_name
            != TARGET_VARIABLE
        ):
            # Processamento normal.
            # poll_once() fará commit.
            return

        target_seen += 1

        if target_seen == 1:
            # Primeiro cane_flow é concluído
            # com sucesso.
            #
            # Isso estabelece um committed
            # offset nesta partition.
            first_committed_observation = (
                observation
            )

            return

        # Segundo cane_flow representa
        # nossa falha de processamento.
        failed_observation = (
            observation
        )

        raise ExpectedProcessingFailure(
            "Intentional failure "
            "before offset commit."
        )

    failure_observed = False

    try:
        deadline = (
            time.monotonic()
            + 30.0
        )

        while (
            not failure_observed
            and time.monotonic()
            < deadline
        ):
            try:
                consumer.poll_once(
                    handler=(
                        failing_handler
                    ),
                    timeout=1.0,
                )

            except ExpectedProcessingFailure:
                failure_observed = True

    finally:
        consumer.close()

    assert (
        first_committed_observation
        is not None
    )

    assert failed_observation is not None

    assert failure_observed is True

    assert (
        failed_observation.telemetry_id
        !=
        first_committed_observation.telemetry_id
    )

    # ---------------------------------------------------------
    # Simulated process restart
    #
    # New Consumer object.
    # New Registry client.
    # New decoder/cache.
    #
    # Same Kafka consumer group.
    # ---------------------------------------------------------

    restarted_consumer = (
        build_consumer(
            group_id=group_id,
            bootstrap_servers=(
                bootstrap_servers
            ),
            topic=topic,
            registry_url=registry_url,
        )
    )

    replayed_observation = None

    def recovery_handler(
        observation,
    ):
        nonlocal replayed_observation

        if (
            observation.telemetry_id
            ==
            failed_observation.telemetry_id
        ):
            replayed_observation = (
                observation
            )

    try:
        deadline = (
            time.monotonic()
            + 30.0
        )

        while (
            replayed_observation
            is None
            and time.monotonic()
            < deadline
        ):
            restarted_consumer.poll_once(
                handler=(
                    recovery_handler
                ),
                timeout=1.0,
            )

    finally:
        restarted_consumer.close()

    # ---------------------------------------------------------
    # At-Least-Once proof
    # ---------------------------------------------------------

    assert (
        replayed_observation
        is not None
    )

    assert (
        replayed_observation
        ==
        failed_observation
    )

    assert (
        replayed_observation.telemetry_id
        ==
        failed_observation.telemetry_id
    )

    assert (
        replayed_observation.variable_id
        ==
        failed_observation.variable_id
    )

    assert (
        replayed_observation.observed_at
        ==
        failed_observation.observed_at
    )
