from __future__ import annotations
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from processing_service.apicurio_wire import (
    frame_apicurio_payload,
)

from processing_service.context import (
    ContextTransition,
)

from processing_service.context_avro_codec import (
    ContextTransitionAvroCodec,
)

from processing_service.context_kafka import (
    build_context_key,
)

from processing_service.context_kafka_producer import (
    ContextKafkaDeliveryError,
    ContextKafkaDeliveryPendingError,
    ContextKafkaEnqueueError,
)


class ContextTransitionPublishError(
    RuntimeError
):
    pass


class ContextTransport(
    Protocol
):
    def publish(
        self,
        *,
        key: bytes,
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
class PreparedContextRecord:
    context_transition_id: UUID
    key: bytes
    value: bytes


class ContextTransitionPublisher:
    """
    Publica OperationalContextTransition.
    Serialize + frame acontecem uma única vez
    por chamada, preservando exatamente o mesmo
    record durante retries internos.
    """

    def __init__(
        self,
        *,
        codec: ContextTransitionAvroCodec,
        content_id: int,
        transport: ContextTransport,
        max_attempts: int = 3,
        flush_timeout: float = 10.0,
        retry_backoff_seconds: float = 1.0,
        sleeper: Callable[
            [float],
            None,
        ] = time.sleep,
    ) -> None:

        if content_id <= 0:
            raise ValueError(
                "content_id must be positive."
            )

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
                "cannot be negative."
            )

        self._codec = codec
        self._content_id = content_id
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

    def publish(
        self,
        transition: ContextTransition,
    ) -> None:

        prepared = self._prepare(
            transition
        )

        attempt = 1

        while True:
            try:
                self._transport.publish(
                    key=prepared.key,
                    value=prepared.value,
                )

            except ContextKafkaEnqueueError as exc:
                if attempt >= (
                    self._max_attempts
                ):
                    raise (
                        ContextTransitionPublishError(
                            "Context transition "
                            "enqueue failed after "
                            f"{attempt} attempt(s)."
                        )
                    ) from exc

                self._wait_before_retry()

                attempt += 1
                continue

            try:
                self._wait_for_delivery()

                return

            except ContextKafkaDeliveryError as exc:
                if attempt >= (
                    self._max_attempts
                ):
                    raise (
                        ContextTransitionPublishError(
                            "Context transition "
                            "delivery failed after "
                            f"{attempt} attempt(s)."
                        )
                    ) from exc

                self._wait_before_retry()

                attempt += 1

    def _prepare(
        self,
        transition: ContextTransition,
    ) -> PreparedContextRecord:

        avro_payload = (
            self._codec.serialize(
                transition
            )
        )

        kafka_value = (
            frame_apicurio_payload(
                content_id=(
                    self._content_id
                ),
                payload=avro_payload,
            )
        )

        key = build_context_key(
            transition
        )

        return PreparedContextRecord(
            context_transition_id=(
                transition
                .context_transition_id
            ),
            key=key,
            value=kafka_value,
        )

    def _wait_for_delivery(
        self,
    ) -> None:

        while True:
            try:
                self._transport.flush(
                    timeout=(
                        self._flush_timeout
                    )
                )

                return

            except (
                ContextKafkaDeliveryPendingError
            ):
                # Mesma mensagem continua
                # pendente. Não republicar.
                continue

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
