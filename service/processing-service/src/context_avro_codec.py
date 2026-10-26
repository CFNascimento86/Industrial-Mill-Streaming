from __future__ import annotations
import json
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import UUID

from datetime import (
    datetime,
    timezone,
)

from fastavro import (
    parse_schema,
    schemaless_reader,
    schemaless_writer,
)

from fastavro.validation import (
    validate,
)

from processing_service.context import (
    ContextOrigin,
    ContextScopeType,
    ContextTransition,
    ContextTransitionType,
)


class ContextAvroContractError(
    ValueError
):
    pass


class ContextTransitionAvroCodec:
    def __init__(
        self,
        schema: dict[str, Any],
    ) -> None:
        try:
            self._schema = (
                parse_schema(
                    deepcopy(
                        schema
                    )
                )
            )

        except Exception as exc:
            raise (
                ContextAvroContractError(
                    "Could not parse "
                    "context Avro schema."
                )
            ) from exc

    @classmethod
    def from_path(
        cls,
        schema_path: str | Path,
    ) -> (
        ContextTransitionAvroCodec
    ):
        path = Path(
            schema_path
        )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            schema = json.load(
                file
            )

        return cls(
            schema
        )

    def serialize(
        self,
        transition: ContextTransition,
    ) -> bytes:

        record = {
            "context_transition_id": str(
                transition
                .context_transition_id
            ),

            "context_logical_name": (
                transition
                .context_logical_name
            ),

            "transition_type": (
                transition
                .transition_type
                .value
            ),

            "previous_state": (
                transition
                .previous_state
            ),

            "current_state": (
                transition
                .current_state
            ),

            "scope_type": (
                transition
                .scope_type
                .value
            ),

            "scope_id": str(
                transition.scope_id
            ),

            "scope_logical_name": (
                transition
                .scope_logical_name
            ),

            "effective_at": (
                transition.effective_at
            ),

            "produced_at": (
                transition.produced_at
            ),

            "origin": (
                transition
                .origin
                .value
            ),

            "evidence_telemetry_ids": [
                str(value)
                for value
                in transition
                .evidence_telemetry_ids
            ],

            "inference_rule_id": (
                transition
                .inference_rule_id
            ),

            "inference_rule_version": (
                transition
                .inference_rule_version
            ),
        }

        validate(
            record,
            self._schema,
            raise_errors=True,
            strict=True,
        )

        buffer = BytesIO()

        schemaless_writer(
            buffer,
            self._schema,
            record,
            strict=True,
        )

        return buffer.getvalue()

    def deserialize(
        self,
        payload: bytes,
    ) -> ContextTransition:

        record = schemaless_reader(
            BytesIO(
                payload
            ),
            self._schema,
        )

        return ContextTransition(
            context_transition_id=UUID(
                str(
                    record[
                        "context_transition_id"
                    ]
                )
            ),

            context_logical_name=(
                record[
                    "context_logical_name"
                ]
            ),

            transition_type=(
                ContextTransitionType(
                    record[
                        "transition_type"
                    ]
                )
            ),

            previous_state=(
                record[
                    "previous_state"
                ]
            ),

            current_state=(
                record[
                    "current_state"
                ]
            ),

            scope_type=(
                ContextScopeType(
                    record[
                        "scope_type"
                    ]
                )
            ),

            scope_id=UUID(
                str(
                    record[
                        "scope_id"
                    ]
                )
            ),

            scope_logical_name=(
                record[
                    "scope_logical_name"
                ]
            ),

            effective_at=(
                _normalize_timestamp(
                    record[
                        "effective_at"
                    ]
                )
            ),

            produced_at=(
                _normalize_timestamp(
                    record[
                        "produced_at"
                    ]
                )
            ),

            origin=(
                ContextOrigin(
                    record[
                        "origin"
                    ]
                )
            ),

            evidence_telemetry_ids=tuple(
                UUID(
                    str(value)
                )
                for value
                in record[
                    "evidence_telemetry_ids"
                ]
            ),

            inference_rule_id=(
                record[
                    "inference_rule_id"
                ]
            ),

            inference_rule_version=(
                record[
                    "inference_rule_version"
                ]
            ),
        )


def _normalize_timestamp(
    value: datetime | int,
) -> datetime:

    if isinstance(
        value,
        datetime,
    ):
        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    if isinstance(
        value,
        int,
    ):
        return datetime.fromtimestamp(
            value / 1000.0,
            tz=timezone.utc,
        )

    raise ContextAvroContractError(
        "Unsupported timestamp "
        "representation."
    )
