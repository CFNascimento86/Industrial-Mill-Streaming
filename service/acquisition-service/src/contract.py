from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class TelemetryQuality(StrEnum):
    GOOD = "GOOD"
    UNCERTAIN = "UNCERTAIN"
    BAD = "BAD"
    UNKNOWN = "UNKNOWN"


class ObservedAtSource(StrEnum):
    SOURCE = "SOURCE"
    ACQUISITION = "ACQUISITION"


@dataclass(frozen=True)
class TelemetryObservation:
    """
    Representa uma observação industrial formalizada
    na fronteira semântica do IMS.
    """

    telemetry_id: UUID

    variable_id: UUID
    variable_logical_name: str

    source_id: UUID
    source_logical_name: str

    value: float
    quality: TelemetryQuality

    observed_at: datetime
    observed_at_source: ObservedAtSource

    ingested_at: datetime
