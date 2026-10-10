from __future__ import annotations
from copy import deepcopy
import json
from datetime import (
    datetime,
    timezone,
)
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import UUID

from fastavro import (
    parse_schema,
    schemaless_reader,
    schemaless_writer,
)
from fastavro.validation import validate

from acquisition_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)


class AvroContractError(ValueError):
    pass


class TelemetryAvroCodec:
    """
    Valida, serializa e desserializa
    TelemetryObservation utilizando Avro.
    """

    def __init__(
        self,
        schema: dict[str, Any],
    ) -> None:
        if not isinstance(
            schema,
            dict,
        ):
            raise AvroContractError(
                "Avro schema must be a dictionary."
            )

        try:
            self._schema = parse_schema(
                deepcopy(schema)
            )

        except Exception as exc:
            raise AvroContractError(
                "Could not parse Avro schema."
            ) from exc

    @classmethod
    def from_path(
        cls,
        schema_path: str | Path,
    ) -> TelemetryAvroCodec:
        path = Path(
            schema_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Avro schema '{path}' "
                "was not found."
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            raw_schema = json.load(
                file
            )

        return cls(
            raw_schema
        )

    @classmethod
    def from_json_text(
        cls,
        schema_text: str,
    ) -> TelemetryAvroCodec:
        try:
            raw_schema = json.loads(
                schema_text
            )

        except json.JSONDecodeError as exc:
            raise AvroContractError(
                "Invalid Avro schema JSON."
            ) from exc

        if not isinstance(
            raw_schema,
            dict,
        ):
            raise AvroContractError(
                "Avro schema must be a JSON object."
            )

        return cls(
            raw_schema
        )


def _to_avro_record(
    observation: TelemetryObservation,
) -> dict[str, Any]:
    return {
        "telemetry_id": str(
            observation.telemetry_id
        ),

        "variable_id": str(
            observation.variable_id
        ),

        "variable_logical_name": (
            observation.variable_logical_name
        ),

        "source_id": str(
            observation.source_id
        ),

        "source_logical_name": (
            observation.source_logical_name
        ),

        "value": observation.value,

        "quality": (
            observation.quality.value
        ),

        "observed_at": (
            observation.observed_at
        ),

        "observed_at_source": (
            observation
            .observed_at_source
            .value
        ),

        "ingested_at": (
            observation.ingested_at
        ),
    }


def _from_avro_record(
    record: dict[str, Any],
) -> TelemetryObservation:
    return TelemetryObservation(
        telemetry_id=UUID(
            str(record["telemetry_id"])
        ),

        variable_id=UUID(
            str(record["variable_id"])
        ),

        variable_logical_name=(
            record["variable_logical_name"]
        ),

        source_id=UUID(
            str(record["source_id"])
        ),

        source_logical_name=(
            record["source_logical_name"]
        ),

        value=float(
            record["value"]
        ),

        quality=TelemetryQuality(
            record["quality"]
        ),

        observed_at=_normalize_timestamp(
            record["observed_at"]
        ),

        observed_at_source=(
            ObservedAtSource(
                record["observed_at_source"]
            )
        ),

        ingested_at=_normalize_timestamp(
            record["ingested_at"]
        ),
    )


def _normalize_timestamp(
    value: datetime | int,
) -> datetime:
    """
    Normaliza o retorno da biblioteca para UTC.
    fastavro possui suporte nativo a timestamp-millis,
    mas mantemos fallback para o tipo físico long.
    """

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

    raise AvroContractError(
        "Unsupported timestamp representation: "
        f"{type(value).__name__}"
    )
