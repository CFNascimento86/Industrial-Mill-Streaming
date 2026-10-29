from __future__ import annotations
from datetime import datetime, timezone,
from pathlib import Path
from uuid import UUID

from processing_service.context import (
    ContextOrigin,
    ContextScopeType,
    ContextTransition,
    ContextTransitionType,
)

from processing_service.context_avro_codec import (
    ContextTransitionAvroCodec,
)

from processing_service.context_kafka_producer import (
    ContextKafkaDeliveryError,
    ContextKafkaDeliveryPendingError,
)

from processing_service.context_publisher import (
    ContextTransitionPublisher,
)


REPOSITORY_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

SCHEMA_PATH = (
    REPOSITORY_ROOT
    / "contracts"
    / "context"
    / "operational-context-transition-v1.avsc"
)


class FakeTransport:
    def __init__(
        self,
        *,
        flush_results,
    ):
        self.flush_results = list(
            flush_results
        )

        self.publications = []
        self.flush_count = 0

    def publish(
        self,
        *,
        key,
        value,
    ):
        self.publications.append(
            (
                key,
                value,
            )
        )

    def flush(
        self,
        *,
        timeout,
    ):
        self.flush_count += 1

        result = (
            self.flush_results.pop(0)
        )

        if isinstance(
            result,
            Exception,
        ):
            raise result


def make_transition():
    return ContextTransition(
        context_transition_id=UUID(
            "11111111-1111-4111-8111-111111111111"
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
            "22222222-2222-4222-8222-222222222222"
        ),

        scope_logical_name="milling",

        effective_at=datetime(
            2026,
            10,
            29,
            12,
            0,
            0,
            123000,
            tzinfo=timezone.utc,
        ),

        produced_at=datetime(
            2026,
            10,
            29,
            12,
            0,
            0,
            456000,
            tzinfo=timezone.utc,
        ),

        origin=(
            ContextOrigin.INFERRED
        ),

        evidence_telemetry_ids=(
            UUID(
                "33333333-3333-4333-8333-333333333333"
            ),
        ),

        inference_rule_id=(
            "milling_feed_load_condition"
        ),

        inference_rule_version="1.0",
    )


def build_codec():
    return (
        ContextTransitionAvroCodec
        .from_path(
            SCHEMA_PATH
        )
    )


def test_pending_delivery_does_not_republish():
    transport = FakeTransport(
        flush_results=[
            ContextKafkaDeliveryPendingError(
                "pending"
            ),
            None,
        ]
    )

    publisher = (
        ContextTransitionPublisher(
            codec=build_codec(),
            content_id=17,
            transport=transport,
            retry_backoff_seconds=0,
        )
    )

    publisher.publish(
        make_transition()
    )

    assert len(
        transport.publications
    ) == 1

    assert transport.flush_count == 2


def test_final_delivery_failure_reuses_same_record():
    transport = FakeTransport(
        flush_results=[
            ContextKafkaDeliveryError(
                "delivery failed"
            ),
            None,
        ]
    )

    publisher = (
        ContextTransitionPublisher(
            codec=build_codec(),
            content_id=17,
            transport=transport,
            max_attempts=2,
            retry_backoff_seconds=0,
        )
    )

    publisher.publish(
        make_transition()
    )

    assert len(
        transport.publications
    ) == 2

    first_key, first_value = (
        transport.publications[0]
    )

    second_key, second_value = (
        transport.publications[1]
    )

    assert first_key == second_key
    assert first_value == second_value
