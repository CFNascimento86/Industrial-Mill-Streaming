from __future__ import annotations
import pytest
import os
import time

from datetime import (
    datetime,
    timezone,
)

from uuid import (
    UUID,
    uuid4,
)

from confluent_kafka import (
    Consumer,
    TopicPartition,
)

from processing_service.apicurio_wire import (
    parse_apicurio_payload,
)

from processing_service.context import (
    ContextOrigin,
    ContextScopeType,
    ContextTransition,
    ContextTransitionType,
)

from processing_service.context_avro_codec import (
    ContextTransitionAvroCodec,
)

from processing_service.context_kafka import (
    build_context_key,
)

from processing_service.context_kafka_producer import (
    KafkaContextProducer,
)

from processing_service.context_publisher import (
    ContextTransitionPublisher,
)

from processing_service.registry_client import (
    ApicurioRegistryClient,
)


RUN_TEST = (
    os.getenv(
        "RUN_CONTEXT_PUBLISHER_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_TEST,
        reason=(
            "Context publisher integration "
            "test is disabled."
        ),
    ),
]


def make_transition():
    return ContextTransition(
        context_transition_id=UUID(
            "77777777-7777-4777-8777-777777777777"
        ),
        context_logical_name=(
            "milling_feed_load_condition"
        ),
        transition_type=(
            ContextTransitionType.CHANGED
        ),
        previous_state="NORMAL",
        current_state="HIGH",
        scope_type=(
            ContextScopeType.PROCESS
        ),
        scope_id=UUID(
            "88888888-8888-4888-8888-888888888888"
        ),
        scope_logical_name="milling",
        effective_at=datetime(
            2026,
            10,
            29,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        produced_at=datetime(
            2026,
            10,
            29,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
        origin=(
            ContextOrigin.INFERRED
        ),
        evidence_telemetry_ids=(
            UUID(
                "99999999-9999-4999-8999-999999999999"
            ),
        ),
        inference_rule_id=(
            "milling_feed_load_condition"
        ),
        inference_rule_version="1.0",
    )


def test_context_transition_reaches_kafka():
    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )

    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        "http://localhost:8080/apis/registry/v3",
    )

    topic = os.getenv(
        "KAFKA_CONTEXT_TOPIC",
        "ims.context.transition",
    )

    registry = (
        ApicurioRegistryClient(
            registry_url
        )
    )

    contract = (
        registry.resolve_avro_contract(
            group_id="ims.context",
            artifact_id=(
                "operational-context-transition"
            ),
            version="1.0.0",
        )
    )

    codec = (
        ContextTransitionAvroCodec(
            contract.schema
        )
    )

    producer = KafkaContextProducer(
        bootstrap_servers=(
            bootstrap_servers
        ),
        topic=topic,
    )

    publisher = (
        ContextTransitionPublisher(
            codec=codec,
            content_id=(
                contract.content_id
            ),
            transport=producer,
        )
    )

    consumer = Consumer(
        {
            "bootstrap.servers": (
                bootstrap_servers
            ),
            "group.id": (
                "ims-context-test-"
                f"{uuid4()}"
            ),
            "enable.auto.commit": False,
        }
    )

    metadata = consumer.list_topics(
        topic=topic,
        timeout=5.0,
    )

    start_offsets = []

    for partition_id in sorted(
        metadata
        .topics[topic]
        .partitions
    ):
        tp = TopicPartition(
            topic,
            partition_id,
        )

        _, high = (
            consumer
            .get_watermark_offsets(
                tp,
                timeout=5.0,
            )
        )

        start_offsets.append(
            TopicPartition(
                topic,
                partition_id,
                high,
            )
        )

    consumer.assign(
        start_offsets
    )

    expected = make_transition()

    publisher.publish(
        expected
    )

    received = None
    received_message = None

    try:
        deadline = (
            time.monotonic()
            + 10.0
        )

        while (
            received is None
            and time.monotonic()
            < deadline
        ):
            message = consumer.poll(
                0.5
            )

            if message is None:
                continue

            if message.error():
                raise AssertionError(
                    message.error()
                )

            framed = (
                parse_apicurio_payload(
                    message.value()
                )
            )

            candidate = (
                codec.deserialize(
                    framed.payload
                )
            )

            if (
                candidate
                .context_transition_id
                != expected
                .context_transition_id
            ):
                continue

            assert (
                framed.content_id
                == contract.content_id
            )

            received = candidate
            received_message = message

    finally:
        consumer.close()

    assert received == expected

    assert (
        received_message.key()
        == build_context_key(
            expected
        )
    )
