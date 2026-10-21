from __future__ import annotations
import time

from collections.abc import (
    Callable,
    Iterable,
)
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from .apicurio_wire import (
    ApicurioWireFramer,
)
from .avro_codec import (
    TelemetryAvroCodec,
)
from .contract import (
    TelemetryObservation,
)
from .kafka_producer import (
    KafkaDeliveryError,
    KafkaDeliveryPendingError,
    KafkaEnqueueError,
)


class TelemetryBatchPublishError(
    RuntimeError
):
    """
    O batch de telemetria não pôde
    ser publicado após as tentativas
    permitidas.
    """


class TelemetryTransport(
    Protocol
):
    def publish(
        self,
        *,
        variable_id: UUID,
        value: bytes,
    ) -> None:
        ...

    def flush(
        self,
        *,
        timeout: float = 10.0,
    ) -> None:
        ...


@dataclass(
    frozen=True,
    slots=True,
)
class PreparedTelemetryRecord:
    """
    Registro imutável preparado para Kafka.
    Depois de criado, retries reutilizam
    exatamente os mesmos bytes.
    """

    telemetry_id: UUID
    variable_id: UUID
    value: bytes


class TelemetryPublisher:
    """
    Fronteira entre TelemetryObservation
    e o transporte Kafka.

    Responsabilidades:
    - serializar Avro;
    - aplicar framing Apicurio;
    - preservar o batch preparado;
    - publicar no transporte;
    - tratar delivery pending;
    - executar bounded retry somente
      após falha definitiva.
    """

    def __init__(
        self,
        *,
        codec: TelemetryAvroCodec,
        framer: ApicurioWireFramer,
        transport: TelemetryTransport,
        max_attempts: int = 3,
        flush_timeout: float = 10.0,
        retry_backoff_seconds: float = 1.0,
        sleeper: Callable[
            [float],
            None,
        ] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError(
                "max_attempts must be >= 1."
            )

        if flush_timeout <= 0:
            raise ValueError(
                "flush_timeout must be positive."
            )

        if retry_backoff_seconds < 0:
            raise ValueError(
                "retry_backoff_seconds "
                "must not be negative."
            )

        self._codec = codec
        self._framer = framer
        self._transport = transport

        self._max_attempts = (
            max_attempts
        )

        self._flush_timeout = (
            flush_timeout
        )

        self._retry_backoff_seconds = (
            retry_backoff_seconds
        )

        self._sleeper = sleeper

    def publish_batch(
        self,
        observations: Iterable[
            TelemetryObservation
        ],
    ) -> int:
        """
        Publica um batch preservando
        sua identidade durante retries.
        O batch é preparado apenas uma vez.
        """

        prepared = self._prepare_batch(
            observations
        )

        if not prepared:
            return 0

        attempt = 1

        while True:
            try:
                self._enqueue_batch(
                    prepared
                )

            except KafkaEnqueueError as exc:
                self._settle_pending()

                if attempt >= (
                    self._max_attempts
                ):
                    raise (
                        TelemetryBatchPublishError(
                            "Telemetry batch "
                            "enqueue failed after "
                            f"{attempt} attempt(s)."
                        )
                    ) from exc

                self._wait_before_retry()

                attempt += 1
                continue

            try:
                self._wait_for_delivery()

                return len(prepared)

            except KafkaDeliveryError as exc:
                if attempt >= (
                    self._max_attempts
                ):
                    raise (
                        TelemetryBatchPublishError(
                            "Telemetry batch "
                            "delivery failed after "
                            f"{attempt} attempt(s)."
                        )
                    ) from exc

                self._wait_before_retry()

                attempt += 1

    def _prepare_batch(
        self,
        observations: Iterable[
            TelemetryObservation
        ],
    ) -> tuple[
        PreparedTelemetryRecord,
        ...,
    ]:
        """
        Serializa e aplica framing uma
        única vez antes de qualquer retry.
        """

        prepared = []

        for observation in observations:
            avro_payload = (
                self._codec.serialize(
                    observation
                )
            )

            kafka_value = (
                self._framer.frame(
                    avro_payload
                )
            )

            prepared.append(
                PreparedTelemetryRecord(
                    telemetry_id=(
                        observation.telemetry_id
                    ),
                    variable_id=(
                        observation.variable_id
                    ),
                    value=kafka_value,
                )
            )

        return tuple(
            prepared
        )

    def _enqueue_batch(
        self,
        prepared: tuple[
            PreparedTelemetryRecord,
            ...,
        ],
    ) -> None:
        for record in prepared:
            self._transport.publish(
                variable_id=(
                    record.variable_id
                ),
                value=record.value,
            )

    def _wait_for_delivery(
        self,
    ) -> None:
        """
        Aguarda o mesmo conjunto já
        enfileirado.
        Timeout não causa republicação.
        """

        while True:
            try:
                self._transport.flush(
                    timeout=(
                        self._flush_timeout
                    )
                )

                return

            except (
                KafkaDeliveryPendingError
            ):
                continue

    def _settle_pending(
        self,
    ) -> None:
        """
        Antes de uma republicação após
        enqueue parcial, resolve tudo que
        já havia sido colocado no producer.
        Isso reduz a criação desnecessária
        de mensagens simultaneamente
        pendentes.
        """

        while True:
            try:
                self._transport.flush(
                    timeout=(
                        self._flush_timeout
                    )
                )

                return

            except (
                KafkaDeliveryPendingError
            ):
                continue

            except KafkaDeliveryError:
                # As mensagens anteriores já
                # alcançaram estado final.
                return

    def _wait_before_retry(
        self,
    ) -> None:
        if (
            self._retry_backoff_seconds
            == 0
        ):
            return

        self._sleeper(
            self._retry_backoff_seconds
        )
