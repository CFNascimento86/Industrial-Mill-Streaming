from __future__ import annotations
from threading import Lock
from uuid import UUID

from confluent_kafka import (
    KafkaError,
    KafkaException,
    Message,
    Producer,
)


DEFAULT_TELEMETRY_TOPIC = (
    "ims.telemetry.observation"
)


class KafkaPublishError(
    RuntimeError
):
    """Erro base de publicação Kafka."""


class KafkaEnqueueError(
    KafkaPublishError
):
    """
    A mensagem não pôde ser colocada
    na fila local do producer.
    """


class KafkaDeliveryError(
    KafkaPublishError
):
    """
    Uma ou mais mensagens receberam
    falha definitiva de delivery.
    """


class KafkaDeliveryPendingError(
    KafkaPublishError
):
    """
    O flush expirou, mas ainda existem
    mensagens pendentes no producer.
    """


class KafkaTelemetryProducer:
    """
    Transporte Kafka das observações
    de telemetria do IMS.
    """

    def __init__(
        self,
        *,
        bootstrap_servers: str,
        topic: str = (
            DEFAULT_TELEMETRY_TOPIC
        ),
        client_id: str = (
            "ims-acquisition-service"
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

    @staticmethod
    def build_key(
        variable_id: UUID,
    ) -> bytes:
        if not isinstance(
            variable_id,
            UUID,
        ):
            raise TypeError(
                "variable_id must be UUID."
            )

        return str(
            variable_id
        ).encode(
            "utf-8"
        )

    def publish(
        self,
        *,
        variable_id: UUID,
        value: bytes,
    ) -> None:
        if not isinstance(
            value,
            bytes,
        ):
            raise TypeError(
                "value must be bytes."
            )

        if not value:
            raise ValueError(
                "value must not be empty."
            )

        key = self.build_key(
            variable_id
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
            raise KafkaEnqueueError(
                "Kafka message could not "
                "be queued."
            ) from exc

        self._producer.poll(0)

    def flush(
        self,
        *,
        timeout: float = 10.0,
    ) -> None:
        """
        Aguarda as mensagens pendentes.

        Importante:
        timeout != delivery failure.

        Se ainda existirem mensagens na fila
        ao final do timeout, elas permanecem
        pendentes e flush() pode ser chamado
        novamente.
        """

        if timeout <= 0:
            raise ValueError(
                "timeout must be positive."
            )

        remaining = (
            self._producer.flush(
                timeout
            )
        )

        with self._delivery_lock:
            delivery_errors = tuple(
                self._delivery_errors
            )

            self._delivery_errors.clear()

        if delivery_errors:
            details = "; ".join(
                delivery_errors
            )

            raise KafkaDeliveryError(
                "Kafka delivery failed: "
                f"{details}"
            )

        if remaining != 0:
            raise (
                KafkaDeliveryPendingError(
                    "Kafka delivery is still "
                    f"pending for {remaining} "
                    "message(s)."
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
