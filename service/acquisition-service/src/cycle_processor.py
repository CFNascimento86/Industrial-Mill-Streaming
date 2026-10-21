from __future__ import annotations

from acquisition_service.contract import (
    TelemetryObservation,
)
from acquisition_service.model import (
    AcquisitionReading,
)
from acquisition_service.telemetry_publisher import (
    TelemetryPublisher,
)
from acquisition_service.transformer import (
    TelemetryTransformer,
)


class TelemetryCycleProcessor:
    """
    Orquestra a fronteira:

        AcquisitionReading
            ↓
        TelemetryObservation
            ↓
        TelemetryPublisher

    O método process() somente retorna
    depois que o batch foi concluído
    pelo publisher.
    """

    def __init__(
        self,
        *,
        transformer: TelemetryTransformer,
        publisher: TelemetryPublisher,
    ) -> None:
        self._transformer = transformer
        self._publisher = publisher

    def process(
        self,
        readings: tuple[
            AcquisitionReading,
            ...,
        ],
    ) -> tuple[
        TelemetryObservation,
        ...,
    ]:
        observations = tuple(
            self._transformer.transform(
                reading
            )
            for reading in readings
        )

        self._publisher.publish_batch(
            observations
        )

        return observations
