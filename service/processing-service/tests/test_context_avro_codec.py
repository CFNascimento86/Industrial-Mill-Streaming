from __future__ import annotations
from pathlib import Path
from uuid import UUID

from datetime import (
    datetime,
    timezone,
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

        scope_logical_name=(
            "milling"
        ),

        effective_at=datetime(
            2026,
            10,
            26,
            12,
            0,
            0,
            123000,
            tzinfo=timezone.utc,
        ),

        produced_at=datetime(
            2026,
            10,
            26,
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


def test_context_avro_round_trip():
    codec = (
        ContextTransitionAvroCodec
        .from_path(
            SCHEMA_PATH
        )
    )

    original = (
        make_transition()
    )

    payload = codec.serialize(
        original
    )

    restored = codec.deserialize(
        payload
    )

    assert restored == original


def test_context_key_is_stable():
    transition = (
        make_transition()
    )

    first = build_context_key(
        transition
    )

    second = build_context_key(
        transition
    )

    assert first == second

    assert first == (
        b"PROCESS:"
        b"22222222-2222-4222-8222-222222222222:"
        b"milling_feed_load_condition"
    )
