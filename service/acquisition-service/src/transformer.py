from __future__ import annotations
import math
from collections.abc import Callable
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import (
    UUID,
    uuid4,
)

from acquisition_service.contract import (
    ObservedAtSource,
    TelemetryObservation,
    TelemetryQuality,
)
from acquisition_service.identity import (
    IdentityResolver,
)
from acquisition_service.model import (
    AcquisitionReading,
)


class TelemetryTransformationError(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


class TelemetryTransformer:
    """
    Transforma AcquisitionReading em TelemetryObservation.
    Esta classe representa a fronteira entre:

        source-specific acquisition

    e:

        source-agnostic industrial telemetry
    """

    def __init__(
        self,
        *,
        identity_resolver: IdentityResolver,
        source_logical_name: str,
        id_factory: Callable[[], UUID] = uuid4,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        if not source_logical_name.strip():
            raise TelemetryTransformationError(
                "Source logical name cannot be empty."
            )

        self._identity_resolver = (
            identity_resolver
        )

        self._source_logical_name = (
            source_logical_name
        )

        self._id_factory = id_factory
        self._clock = clock

    def transform(
        self,
        reading: AcquisitionReading,
    ) -> TelemetryObservation:
        """
        Transforma uma única leitura adquirida
        em uma observação industrial contratada.
        """

        if not math.isfinite(
            reading.value
        ):
            raise TelemetryTransformationError(
                f"Value for '{reading.logical_name}' "
                "must be finite."
            )

        _require_utc(
            reading.observed_at,
            field_name="observed_at",
        )

        try:
            quality = TelemetryQuality(
                reading.quality
            )
        except ValueError as exc:
            raise TelemetryTransformationError(
                f"Unsupported telemetry quality: "
                f"{reading.quality}"
            ) from exc

        identity = (
            self._identity_resolver.resolve(
                variable_logical_name=(
                    reading.logical_name
                ),
                source_logical_name=(
                    self._source_logical_name
                ),
            )
        )

        ingested_at = self._clock()

        _require_utc(
            ingested_at,
            field_name="ingested_at",
        )

        return TelemetryObservation(
            telemetry_id=self._id_factory(),

            variable_id=identity.variable_id,
            variable_logical_name=(
                identity.variable_logical_name
            ),

            source_id=identity.source_id,
            source_logical_name=(
                identity.source_logical_name
            ),

            value=reading.value,
            quality=quality,

            observed_at=(
                reading.observed_at
            ),

            observed_at_source=(
                ObservedAtSource.ACQUISITION
            ),

            ingested_at=ingested_at,
        )


def _require_utc(
    value: datetime,
    *,
    field_name: str,
) -> None:
    if value.tzinfo is None:
        raise TelemetryTransformationError(
            f"'{field_name}' must be timezone-aware."
        )

    if value.utcoffset() != timedelta(0):
        raise TelemetryTransformationError(
            f"'{field_name}' must be UTC."
        )
