from __future__ import annotations

import os
import subprocess
import threading
import time

from datetime import (
    datetime,
    timezone,
)
from uuid import (
    UUID,
    uuid4,
)

import pytest

from confluent_kafka import (
    Consumer,
    TopicPartition,
)

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
    DEFAULT_TELEMETRY_TOPIC,
    KafkaTelemetryProducer,
)
from acquisition_service.telemetry_publisher import (
    TelemetryPublisher,
)


RUN_KAFKA_RECOVERY_TESTS = (
    os.getenv(
        "RUN_KAFKA_RECOVERY_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_KAFKA_RECOVERY_TESTS,
        reason=(
            "Kafka recovery integration test "
            "requires "
            "RUN_KAFKA_RECOVERY_INTEGRATION_TESTS=1."
        ),
    ),
]


VARIABLE_ID = UUID(
    "11111111-1111-4111-8111-111111111111"
)

SOURCE_ID = UUID(
    "22222222-2222-4222-8222-222222222222"
)

TELEMETRY_ID = UUID(
    "44444444-4444-4444-8444-444444444444"
)


class CountingTransport:
    """
    Decorator utilizado apenas pelo teste.

    Permite comprovar quantas vezes
    publish() foi realmente chamado.
    """

    def __init__(
        self,
        transport,
    ):
        self._transport = transport

        self.publish_count = 0

        self.published_values = []

    def publish(
        self,
        *,
        variable_id,
        value,
    ):
        self.publish_count += 1

        self.published_values.append(
            (
                variable_id,
                value,
            )
        )

        self._transport.publish(
            variable_id=variable_id,
            value=value,
        )

    def flush(
        self,
        *,
        timeout=10.0,
    ):
        self._transport.flush(
            timeout=timeout
        )


def _docker(
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "docker",
            *args,
        ],
        check=check,
        capture_output=True,
        text=True,
    )


def _start_kafka(
    container_name: str,
) -> None:
    _docker(
        "start",
        container_name,
    )


def _stop_kafka(
    container_name: str,
) -> None:
    _docker(
        "stop",
        container_name,
    )


def _wait_for_kafka(
    *,
    container_name: str,
    timeout: float = 30.0,
) -> None:
    deadline = (
        time.monotonic()
        + timeout
    )

    while (
        time.monotonic()
        < deadline
    ):
        result = _docker(
            "exec",
            container_name,
            (
                "/opt/kafka/bin/"
                "kafka-broker-api-versions.sh"
            ),
            "--bootstrap-server",
            "localhost:9092",
            check=False,
        )

        if result.returncode == 0:
            return

        time.sleep(
            0.5
        )

    raise AssertionError(
        "Kafka did not become ready "
        f"within {timeout} seconds."
    )


def _make_observation(
) -> TelemetryObservation:
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
            17,
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
            17,
            0,
            0,
            125000,
            tzinfo=timezone.utc,
        ),
    )


def _capture_topic_end_offsets(
    *,
    bootstrap_servers: str,
    topic: str,
) -> list[TopicPartition]:
    consumer = Consumer(
        {
            "bootstrap.servers": (
                bootstrap_servers
            ),
            "group.id": (
                "ims-offset-probe-"
                f"{uuid4()}"
            ),
            "enable.auto.commit": False,
        }
    )

    try:
        metadata = consumer.list_topics(
            topic=topic,
            timeout=5.0,
        )

        topic_metadata = (
            metadata.topics[
                topic
            ]
        )

        assert (
            topic_metadata.error
            is None
        )

        assignment = []

        for partition_id in sorted(
            topic_metadata.partitions
        ):
            partition = TopicPartition(
                topic,
                partition_id,
            )

            (
                _low,
                high,
            ) = (
                consumer
                .get_watermark_offsets(
                    partition,
                    timeout=5.0,
                )
            )

            assignment.append(
                TopicPartition(
                    topic,
                    partition_id,
                    high,
                )
            )

        return assignment

    finally:
        consumer.close()


def test_pending_batch_survives_kafka_interruption(
    telemetry_schema_path,
):
    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )

    topic = os.getenv(
        "KAFKA_TELEMETRY_TOPIC",
        DEFAULT_TELEMETRY_TOPIC,
    )

    kafka_container = os.getenv(
        "KAFKA_CONTAINER_NAME",
        "ims-kafka",
    )

    # ---------------------------------------------------------
    # Initial Kafka state
    # ---------------------------------------------------------

    _start_kafka(
        kafka_container
    )

    _wait_for_kafka(
        container_name=(
            kafka_container
        )
    )

    start_offsets = (
        _capture_topic_end_offsets(
            bootstrap_servers=(
                bootstrap_servers
            ),
            topic=topic,
        )
    )

    # ---------------------------------------------------------
    # Publisher components
    # ---------------------------------------------------------

    codec = (
        TelemetryAvroCodec
        .from_path(
            telemetry_schema_path
        )
    )

    framer = ApicurioWireFramer(
        content_id=17
    )

    kafka_transport = (
        KafkaTelemetryProducer(
            bootstrap_servers=(
                bootstrap_servers
            ),
            topic=topic,
            client_id=(
                "ims-kafka-recovery-test"
            ),
        )
    )

    counting_transport = (
        CountingTransport(
            kafka_transport
        )
    )

    publisher = TelemetryPublisher(
        codec=codec,
        framer=framer,
        transport=(
            counting_transport
        ),

        # flush curto para provar que
        # timeout não causa republicação.
        flush_timeout=0.5,

        max_attempts=3,

        retry_backoff_seconds=(
            0.1
        ),
    )

    observation = (
        _make_observation()
    )

    result_holder = {}
    error_holder = {}

    def publish_worker():
        try:
            result_holder[
                "count"
            ] = (
                publisher
                .publish_batch(
                    [observation]
                )
            )

        except Exception as exc:
            error_holder[
                "error"
            ] = exc

    worker = threading.Thread(
        target=publish_worker,
        daemon=True,
    )

    try:
        # -----------------------------------------------------
        # Broker interruption
        # -----------------------------------------------------

        _stop_kafka(
            kafka_container
        )

        worker.start()

        # Tempo suficiente para pelo menos
        # um flush(timeout=0.5) expirar.
        time.sleep(
            1.5
        )

        # O batch deve continuar bloqueado
        # aguardando o MESMO envio.
        assert worker.is_alive()

        # publish() deve ter sido chamado
        # apenas uma vez.
        assert (
            counting_transport
            .publish_count
            == 1
        )

        # -----------------------------------------------------
        # Broker recovery
        # -----------------------------------------------------

        _start_kafka(
            kafka_container
        )

        _wait_for_kafka(
            container_name=(
                kafka_container
            )
        )

        worker.join(
            timeout=20.0
        )

        assert not worker.is_alive()

        assert (
            "error"
            not in error_holder
        )

        assert (
            result_holder["count"]
            == 1
        )

        # Continua sendo exatamente
        # uma chamada de publicação.
        assert (
            counting_transport
            .publish_count
            == 1
        )

        # -----------------------------------------------------
        # Consume from offsets captured before interruption
        # -----------------------------------------------------

        consumer = Consumer(
            {
                "bootstrap.servers": (
                    bootstrap_servers
                ),
                "group.id": (
                    "ims-kafka-recovery-"
                    f"{uuid4()}"
                ),
                "enable.auto.commit": False,
            }
        )

        try:
            consumer.assign(
                start_offsets
            )

            restored = None
            received_message = None

            deadline = (
                time.monotonic()
                + 10.0
            )

            while (
                restored is None
                and time.monotonic()
                < deadline
            ):
                message = consumer.poll(
                    timeout=0.5
                )

                if message is None:
                    continue

                if message.error():
                    raise AssertionError(
                        "Kafka consumer error: "
                        f"{message.error()}"
                    )

                parsed = (
                    ApicurioWireFramer
                    .parse(
                        message.value()
                    )
                )

                candidate = (
                    codec.deserialize(
                        parsed.payload
                    )
                )

                if (
                    candidate.telemetry_id
                    != TELEMETRY_ID
                ):
                    continue

                restored = candidate
                received_message = (
                    message
                )

            assert restored is not None

            assert (
                restored
                == observation
            )

            assert (
                received_message.key()
                == KafkaTelemetryProducer
                .build_key(
                    VARIABLE_ID
                )
            )

            assert (
                restored.telemetry_id
                == TELEMETRY_ID
            )

        finally:
            consumer.close()

    finally:
        # O ambiente deve terminar
        # com Kafka disponível mesmo
        # se alguma assertion falhar.
        _start_kafka(
            kafka_container
        )

        _wait_for_kafka(
            container_name=(
                kafka_container
            )
        )

        if worker.is_alive():
            worker.join(
                timeout=10.0
            )
