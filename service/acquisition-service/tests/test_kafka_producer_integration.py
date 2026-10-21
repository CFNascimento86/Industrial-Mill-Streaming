from __future__ import annotations
import os
import time

from uuid import (
    UUID,
    uuid4,
)

import pytest

from confluent_kafka import (
    Consumer,
    TopicPartition,
)

from acquisition_service.kafka_producer import (
    DEFAULT_TELEMETRY_TOPIC,
    KafkaTelemetryProducer,
)


RUN_KAFKA_INTEGRATION_TESTS = (
    os.getenv(
        "RUN_KAFKA_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_KAFKA_INTEGRATION_TESTS,
        reason=(
            "Kafka integration test requires "
            "RUN_KAFKA_INTEGRATION_TESTS=1."
        ),
    ),
]


def test_same_variable_preserves_partition_and_order():
    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )

    topic = os.getenv(
        "KAFKA_TELEMETRY_TOPIC",
        DEFAULT_TELEMETRY_TOPIC,
    )

    variable_id = UUID(
        "11111111-1111-4111-8111-111111111111"
    )

    expected_key = (
        KafkaTelemetryProducer
        .build_key(
            variable_id
        )
    )

    # Representam dois Kafka-ready values.
    #
    # O framing real Apicurio + Avro
    # já foi validado na fronteira anterior.
    payload_1 = (
        b"\x00"
        b"\x00\x00\x00\x11"
        b"\x02\x04\x06\x08"
    )

    payload_2 = (
        b"\x00"
        b"\x00\x00\x00\x11"
        b"\x0A\x0C\x0E\x10"
    )

    producer = KafkaTelemetryProducer(
        bootstrap_servers=(
            bootstrap_servers
        ),
        topic=topic,
    )

    consumer = Consumer(
        {
            "bootstrap.servers": (
                bootstrap_servers
            ),

            "group.id": (
                "ims-kafka-test-"
                f"{uuid4()}"
            ),

            "enable.auto.commit": False,

            "auto.offset.reset": (
                "latest"
            ),
        }
    )

    try:
        # -----------------------------------------------------
        # Discover topic
        # -----------------------------------------------------

        metadata = (
            consumer.list_topics(
                topic=topic,
                timeout=5.0,
            )
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

        assert len(
            topic_metadata.partitions
        ) == 3

        # -----------------------------------------------------
        # Start exactly at current end of each partition
        # -----------------------------------------------------

        assignment = []

        for partition_id in sorted(
            topic_metadata.partitions
        ):
            topic_partition = (
                TopicPartition(
                    topic,
                    partition_id,
                )
            )

            (
                _low,
                high,
            ) = (
                consumer
                .get_watermark_offsets(
                    topic_partition,
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

        consumer.assign(
            assignment
        )

        # -----------------------------------------------------
        # Produce two observations of same variable
        # -----------------------------------------------------

        producer.publish(
            variable_id=variable_id,
            value=payload_1,
        )

        producer.publish(
            variable_id=variable_id,
            value=payload_2,
        )

        producer.flush(
            timeout=10.0
        )

        # -----------------------------------------------------
        # Consume only records created by this test
        # -----------------------------------------------------

        received = []

        deadline = (
            time.monotonic()
            + 10.0
        )

        while (
            len(received) < 2
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

            if (
                message.key()
                == expected_key
            ):
                received.append(
                    message
                )

        # -----------------------------------------------------
        # Assertions
        # -----------------------------------------------------

        assert len(received) == 2

        assert [
            message.value()
            for message in received
        ] == [
            payload_1,
            payload_2,
        ]

        assert all(
            message.key()
            == expected_key
            for message in received
        )

        partitions = {
            message.partition()
            for message in received
        }

        assert len(partitions) == 1

        assert (
            received[1].offset()
            > received[0].offset()
        )

    finally:
        consumer.close()

        producer.flush(
            timeout=10.0
        )
