from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class FeedLoadCondition(
    StrEnum
):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


@dataclass(
    frozen=True,
    slots=True,
)
class ContextTransition:
    """
    Representa uma mudança inferida
    de condição operacional.
    Ainda não representa a materialização
    física de Context Instance.
    """

    context_name: str

    previous_state: FeedLoadCondition
    current_state: FeedLoadCondition

    effective_at: datetime

    evidence_telemetry_id: UUID
    evidence_variable_id: UUID

    evidence_variable_logical_name: str
    evidence_value: float
