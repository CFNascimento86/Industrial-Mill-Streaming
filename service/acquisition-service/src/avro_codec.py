from __future__ import annotations
import json
from copy import deepcopy
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
    """
    Falha relacionada ao contrato Avro.
    """


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
        """
        Constrói o codec a partir de um arquivo
        Avro local.
        """

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
        """
        Constrói o codec a partir de JSON textual.
        """

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

    @property
    def schema(
        self,
    ) -> dict[str, Any]:
        """
        Retorna o schema Avro parseado.
        """

        return self._schema

    def serialize(
        self,
        observation: TelemetryObservation,
    ) -> bytes:
        """
        Serializa TelemetryObservation
        em Avro binário schemaless.
        """

        record = _to_avro_record(
            observation
        )

        valid = validate(
            record,
            self._schema,
            raise_errors=True,
            strict=True,
        )

        if not valid:
            raise AvroContractError(
                "TelemetryObservation does not "
                "conform to the Avro schema."
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
    ) -> TelemetryObservation:
        """
        Desserializa um payload Avro binário
        para TelemetryObservation.
        """

        buffer = BytesIO(
            payload
        )

        record = schemaless_reader(
            buffer,
            self._schema,
        )

        return _from_avro_record(
            record
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
            str(
                record["telemetry_id"]
            )
        ),

        variable_id=UUID(
            str(
                record["variable_id"]
            )
        ),

        variable_logical_name=(
            record[
                "variable_logical_name"
            ]
        ),

        source_id=UUID(
            str(
                record["source_id"]
            )
        ),

        source_logical_name=(
            record[
                "source_logical_name"
            ]
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
                record[
                    "observed_at_source"
                ]
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
    Normaliza timestamps Avro para UTC.
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
