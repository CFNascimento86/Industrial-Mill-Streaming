from __future__ import annotations

from collections.abc import (
    Callable,
)

from confluent_kafka import (
    Consumer,
    KafkaException,
)

from processing_service.contract import (
    TelemetryObservation,
)
from processing_service.telemetry_decoder import (
    TelemetryMessageDecoder,
)


DEFAULT_TELEMETRY_TOPIC = (
    "ims.telemetry.observation"
)

DEFAULT_PROCESSING_GROUP = (
    "ims-processing"
)


class KafkaRecordContractError(
    RuntimeError
):
    pass


class KafkaTelemetryConsumer:
    def __init__(
        self,
        *,
        bootstrap_servers: str,
        decoder: (
            TelemetryMessageDecoder
        ),
        topic: str = (
            DEFAULT_TELEMETRY_TOPIC
        ),
        group_id: str = (
            DEFAULT_PROCESSING_GROUP
        ),
        auto_offset_reset: str = (
            "latest"
        ),
        consumer_factory=Consumer,
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

        if not group_id:
            raise ValueError(
                "group_id must not be empty."
            )

        if auto_offset_reset not in {
            "earliest",
            "latest",
        }:
            raise ValueError(
                "auto_offset_reset must "
                "be 'earliest' or 'latest'."
            )

        self._topic = topic

        self._decoder = decoder

        self._consumer = (
            consumer_factory(
                {
                    "bootstrap.servers": (
                        bootstrap_servers
                    ),

                    "client.id": (
                        "ims-processing-service"
                    ),

                    "group.id": (
                        group_id
                    ),

                    "enable.auto.commit": (
                        False
                    ),

                    "enable.auto.offset.store": (
                        False
                    ),

                    "auto.offset.reset": (
                        auto_offset_reset
                    ),
                }
            )
        )

        self._consumer.subscribe(
            [
                self._topic
            ]
        )

    def poll_once(
        self,
        *,
        handler: Callable[
            [TelemetryObservation],
            None,
        ],
        timeout: float = 1.0,
    ) -> bool:
        message = (
            self._consumer.poll(
                timeout
            )
        )

        if message is None:
            return False

        if message.error():
            raise KafkaException(
                message.error()
            )

        value = message.value()

        if value is None:
            raise KafkaRecordContractError(
                "Telemetry record "
                "cannot be a tombstone."
            )

        observation = (
            self._decoder.decode(
                value
            )
        )

        expected_key = str(
            observation.variable_id
        ).encode(
            "utf-8"
        )

        if message.key() != (
            expected_key
        ):
            raise KafkaRecordContractError(
                "Kafka key does not "
                "match variable_id."
            )

        # ---------------------------------
        # PROCESS
        # ---------------------------------

        handler(
            observation
        )

        # ---------------------------------
        # Only successful processing
        # advances consumer progress.
        # ---------------------------------

        self._consumer.commit(
            message=message,
            asynchronous=False,
        )

        return True

    def close(
        self,
    ) -> None:
        self._consumer.close()
