from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class FeedLoadCondition(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class ContextTransitionType(StrEnum):
    ESTABLISHED = "ESTABLISHED"
    CHANGED = "CHANGED"


class ContextScopeType(StrEnum):
    PROCESS = "PROCESS"
    ASSET = "ASSET"


class ContextOrigin(StrEnum):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"


@dataclass(
    frozen=True,
    slots=True,
)
class ContextTransition:
    """
    Informação industrial derivada que representa
    o estabelecimento ou mudança de um contexto
    operacional.
    """

    context_transition_id: UUID

    context_logical_name: str

    transition_type: ContextTransitionType

    previous_state: str | None
    current_state: str

    scope_type: ContextScopeType
    scope_id: UUID
    scope_logical_name: str

    effective_at: datetime
    produced_at: datetime

    origin: ContextOrigin

    evidence_telemetry_ids: tuple[
        UUID,
        ...,
    ]

    inference_rule_id: str | None
    inference_rule_version: str | None
