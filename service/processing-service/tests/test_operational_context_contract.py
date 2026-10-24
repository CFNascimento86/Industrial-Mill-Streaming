from __future__ import annotations
import json
from pathlib import Path

from fastavro import (
    parse_schema,
)

from fastavro.schema import (
    fullname,
)

from fastavro.validation import (
    validate,
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


def load_schema():
    with SCHEMA_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def test_operational_context_transition_schema():
    schema = load_schema()

    parsed = parse_schema(
        schema
    )

    assert fullname(
        schema
    ) == (
        "ims.context."
        "OperationalContextTransition"
    )

    assert parsed is not None


def test_established_context_record_is_valid():
    schema = parse_schema(
        load_schema()
    )

    record = {
        "context_transition_id": (
            "33333333-3333-4333-8333-333333333333"
        ),

        "context_logical_name": (
            "milling_feed_load_condition"
        ),

        "transition_type": (
            "ESTABLISHED"
        ),

        "previous_state": None,

        "current_state": (
            "NORMAL"
        ),

        "scope_type": (
            "PROCESS"
        ),

        "scope_id": (
            "11111111-1111-4111-8111-111111111111"
        ),

        "scope_logical_name": (
            "milling"
        ),

        "effective_at": (
            1792843200000
        ),

        "produced_at": (
            1792843200100
        ),

        "origin": (
            "INFERRED"
        ),

        "evidence_telemetry_ids": [
            (
                "22222222-2222-4222-8222-222222222222"
            )
        ],

        "inference_rule_id": (
            "milling_feed_load_condition"
        ),

        "inference_rule_version": (
            "1.0"
        ),
    }

    assert validate(
        record,
        schema,
        strict=True,
    )


def test_changed_context_record_is_valid():
    schema = parse_schema(
        load_schema()
    )

    record = {
        "context_transition_id": (
            "44444444-4444-4444-8444-444444444444"
        ),

        "context_logical_name": (
            "milling_feed_load_condition"
        ),

        "transition_type": (
            "CHANGED"
        ),

        "previous_state": (
            "NORMAL"
        ),

        "current_state": (
            "HIGH"
        ),

        "scope_type": (
            "PROCESS"
        ),

        "scope_id": (
            "11111111-1111-4111-8111-111111111111"
        ),

        "scope_logical_name": (
            "milling"
        ),

        "effective_at": (
            1792843201000
        ),

        "produced_at": (
            1792843201100
        ),

        "origin": (
            "INFERRED"
        ),

        "evidence_telemetry_ids": [
            (
                "55555555-5555-4555-8555-555555555555"
            )
        ],

        "inference_rule_id": (
            "milling_feed_load_condition"
        ),

        "inference_rule_version": (
            "1.0"
        ),
    }

    assert validate(
        record,
        schema,
        strict=True,
    )
