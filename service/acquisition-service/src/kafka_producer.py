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
    """
    Falha ao publicar ou confirmar
    uma mensagem Kafka.
    """


class KafkaTelemetryProducer:
    """
    Producer Kafka responsável pelo transporte
    das observações de telemetria do IMS.
    Esta classe não conhece Avro, Apicurio ou
    o contrato TelemetryObservation.

    Ela recebe:
        - variable_id como chave industrial;
        - bytes já preparados para publicação.

    Responsabilidades:
        - construir a Kafka message key;
        - publicar no tópico de telemetria;
        - acompanhar delivery reports;
        - expor falhas de entrega;
        - confirmar mensagens pendentes.
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

        if not client_id:
            raise ValueError(
                "client_id must not be empty."
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

                "client.id": (
                    client_id
                ),

                # Evita duplicação causada
                # por retries internos do producer.
                "enable.idempotence": True,

                # Confirmação mais forte
                # disponível pelo broker.
                "acks": "all",

                # Mantém compatibilidade de
                # particionamento com o
                # Java Kafka client.
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
        """
        Constrói a chave Kafka canônica.

        Regra IMS:
            variable_id
            -> canonical UUID string
            -> UTF-8
        """

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
        """
        Enfileira uma mensagem para publicação.
        A confirmação física ocorre por meio
        do delivery callback e será verificada
        por flush().
        """

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
            raise KafkaPublishError(
                "Kafka message could not "
                "be queued."
            ) from exc

        # Serve callbacks já disponíveis
        # sem bloquear o fluxo.
        self._producer.poll(0)

    def flush(
        self,
        *,
        timeout: float = 10.0,
    ) -> None:
        """
        Aguarda confirmação das mensagens
        pendentes e propaga falhas de entrega.
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

            raise KafkaPublishError(
                "Kafka delivery failed: "
                f"{details}"
            )

        if remaining != 0:
            raise KafkaPublishError(
                "Kafka flush timed out with "
                f"{remaining} message(s) "
                "still pending."
            )

    def _on_delivery(
        self,
        error: KafkaError | None,
        message: Message,
    ) -> None:
        """
        Recebe o resultado final da entrega
        informado pelo librdkafka.
        """

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
