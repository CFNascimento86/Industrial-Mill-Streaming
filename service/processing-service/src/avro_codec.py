from __future__ import annotations
from copy import deepcopy
from datetime import (
    datetime,
    timezone,
)
from io import BytesIO
from typing import Any
from uuid import UUID

from fastavro import (
    parse_schema,
    schemaless_reader,
)

from processing_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)


class AvroContractError(
    ValueError
):
    pass


class TelemetryAvroDecoder:
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
            raise AvroContractError(
                "Could not parse "
                "Avro schema."
            ) from exc

    def deserialize(
        self,
        payload: bytes,
    ) -> TelemetryObservation:
        if not payload:
            raise AvroContractError(
                "Avro payload "
                "cannot be empty."
            )

        buffer = BytesIO(
            payload
        )

        try:
            record = (
                schemaless_reader(
                    buffer,
                    self._schema,
                )
            )

        except Exception as exc:
            raise AvroContractError(
                "Could not deserialize "
                "TelemetryObservation."
            ) from exc

        return TelemetryObservation(
            telemetry_id=UUID(
                str(
                    record[
                        "telemetry_id"
                    ]
                )
            ),

            variable_id=UUID(
                str(
                    record[
                        "variable_id"
                    ]
                )
            ),

            variable_logical_name=(
                record[
                    "variable_logical_name"
                ]
            ),

            source_id=UUID(
                str(
                    record[
                        "source_id"
                    ]
                )
            ),

            source_logical_name=(
                record[
                    "source_logical_name"
                ]
            ),

            value=float(
                record[
                    "value"
                ]
            ),

            quality=TelemetryQuality(
                record[
                    "quality"
                ]
            ),

            observed_at=(
                _normalize_timestamp(
                    record[
                        "observed_at"
                    ]
                )
            ),

            observed_at_source=(
                ObservedAtSource(
                    record[
                        "observed_at_source"
                    ]
                )
            ),

            ingested_at=(
                _normalize_timestamp(
                    record[
                        "ingested_at"
                    ]
                )
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

    raise AvroContractError(
        "Unsupported timestamp "
        "representation."
    )
