from __future__ import annotations
from threading import Lock

from confluent_kafka import (
    KafkaError,
    KafkaException,
    Message,
    Producer,
)


DEFAULT_CONTEXT_TOPIC = (
    "ims.context.transition"
)


class ContextKafkaPublishError(
    RuntimeError
):
    pass


class ContextKafkaEnqueueError(
    ContextKafkaPublishError
):
    pass


class ContextKafkaDeliveryError(
    ContextKafkaPublishError
):
    pass


class ContextKafkaDeliveryPendingError(
    ContextKafkaPublishError
):
    pass


class KafkaContextProducer:
    """
    Transporte Kafka para informações
    de Operational Context.
    """

    def __init__(
        self,
        *,
        bootstrap_servers: str,
        topic: str = (
            DEFAULT_CONTEXT_TOPIC
        ),
        client_id: str = (
            "ims-processing-service"
        ),
    ) -> None:
        if not bootstrap_servers:
            raise ValueError(
                "bootstrap_servers "
                "must not be empty."
            )

        if not topic:
            raise ValueError(
                "topic must not be empty."
            )

        self._topic = topic

        self._delivery_errors: list[
            str
        ] = []

        self._delivery_lock = Lock()

        self._producer = Producer(
            {
                "bootstrap.servers": (
                    bootstrap_servers
                ),
                "client.id": client_id,
                "enable.idempotence": True,
                "acks": "all",
                "partitioner": (
                    "murmur2_random"
                ),
            }
        )

    @property
    def topic(
        self,
    ) -> str:
        return self._topic

    def publish(
        self,
        *,
        key: bytes,
        value: bytes,
    ) -> None:

        if not isinstance(
            key,
            bytes,
        ) or not key:
            raise ValueError(
                "key must be non-empty bytes."
            )

        if not isinstance(
            value,
            bytes,
        ) or not value:
            raise ValueError(
                "value must be non-empty bytes."
            )

        try:
            self._producer.produce(
                topic=self._topic,
                key=key,
                value=value,
                on_delivery=(
                    self._on_delivery
                ),
            )

        except (
            BufferError,
            KafkaException,
        ) as exc:
            raise (
                ContextKafkaEnqueueError(
                    "Context message could "
                    "not be queued."
                )
            ) from exc

        self._producer.poll(0)

    def flush(
        self,
        *,
        timeout: float = 10.0,
    ) -> None:

        if timeout <= 0:
            raise ValueError(
                "timeout must be positive."
            )

        remaining = (
            self._producer.flush(
                timeout
            )
        )

        # Enquanto ainda existirem records
        # pendentes, não consideramos nenhum
        # resultado final da tentativa.
        if remaining != 0:
            raise (
                ContextKafkaDeliveryPendingError(
                    "Context delivery is still "
                    f"pending for {remaining} "
                    "message(s)."
                )
            )

        with self._delivery_lock:
            delivery_errors = tuple(
                self._delivery_errors
            )

            self._delivery_errors.clear()

        if delivery_errors:
            raise (
                ContextKafkaDeliveryError(
                    "Context delivery failed: "
                    + "; ".join(
                        delivery_errors
                    )
                )
            )

    def _on_delivery(
        self,
        error: KafkaError | None,
        message: Message,
    ) -> None:

        if error is None:
            return

        detail = (
            f"{message.topic()}"
            f"[{message.partition()}]: "
            f"{error}"
        )

        with self._delivery_lock:
            self._delivery_errors.append(
                detail
            )
