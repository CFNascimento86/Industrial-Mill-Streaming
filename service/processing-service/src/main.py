from __future__ import annotations
import logging
import os

from processing_service.kafka_consumer import (
    DEFAULT_PROCESSING_GROUP,
    DEFAULT_TELEMETRY_TOPIC,
    KafkaTelemetryConsumer,
)

from processing_service.registry_client import (
    ApicurioRegistryClient,
)

from processing_service.telemetry_decoder import (
    TelemetryMessageDecoder,
)


DEFAULT_KAFKA_BOOTSTRAP_SERVERS = (
    "localhost:9092"
)

DEFAULT_REGISTRY_URL = (
    "http://localhost:8080/apis/registry/v3"
)

DEFAULT_AUTO_OFFSET_RESET = (
    "earliest"
)

LOG_EVERY_N_OBSERVATIONS = 100


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


def run_processing_service() -> None:
    logger = logging.getLogger(
        "ims.processing"
    )

    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        DEFAULT_KAFKA_BOOTSTRAP_SERVERS,
    )

    topic = os.getenv(
        "KAFKA_TELEMETRY_TOPIC",
        DEFAULT_TELEMETRY_TOPIC,
    )

    group_id = os.getenv(
        "PROCESSING_CONSUMER_GROUP",
        DEFAULT_PROCESSING_GROUP,
    )

    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        DEFAULT_REGISTRY_URL,
    )

    auto_offset_reset = os.getenv(
        "PROCESSING_AUTO_OFFSET_RESET",
        DEFAULT_AUTO_OFFSET_RESET,
    )

    if auto_offset_reset not in {
        "earliest",
        "latest",
    }:
        raise ValueError(
            "PROCESSING_AUTO_OFFSET_RESET "
            "must be 'earliest' or 'latest'."
        )

    # ---------------------------------------------------------
    # Governed contract resolution
    # ---------------------------------------------------------

    registry_client = (
        ApicurioRegistryClient(
            registry_url,
            timeout=5.0,
        )
    )

    decoder = (
        TelemetryMessageDecoder(
            registry_client=(
                registry_client
            )
        )
    )

    # ---------------------------------------------------------
    # Kafka consumer
    # ---------------------------------------------------------

    consumer = (
        KafkaTelemetryConsumer(
            bootstrap_servers=(
                bootstrap_servers
            ),
            topic=topic,
            group_id=group_id,
            auto_offset_reset=(
                auto_offset_reset
            ),
            decoder=decoder,
        )
    )

    processed_count = 0

    def process_observation(
        observation,
    ) -> None:
        """
        Primeiro processing path do IMS.
        Nesta etapa, a responsabilidade
        é validar e reconstruir a informação
        contratada.
        Transformações derivadas serão
        acrescentadas posteriormente.
        """

        nonlocal processed_count

        processed_count += 1

        if (
            processed_count
            % LOG_EVERY_N_OBSERVATIONS
            != 0
        ):
            return

        logger.info(
            "Processed=%d | "
            "variable=%s | "
            "value=%.3f | "
            "quality=%s | "
            "observed_at=%s | "
            "telemetry_id=%s",
            processed_count,
            (
                observation
                .variable_logical_name
            ),
            observation.value,
            observation.quality,
            observation.observed_at,
            observation.telemetry_id,
        )

    logger.info(
        "IMS Processing Service initialized."
    )

    logger.info(
        "Kafka=%s | "
        "Topic=%s | "
        "Group=%s | "
        "Offset reset=%s | "
        "Registry=%s",
        bootstrap_servers,
        topic,
        group_id,
        auto_offset_reset,
        registry_url,
    )

    try:
        while True:
            consumer.poll_once(
                handler=(
                    process_observation
                ),
                timeout=1.0,
            )

    finally:
        consumer.close()


def main() -> None:
    configure_logging()

    logger = logging.getLogger(
        "ims.processing"
    )

    try:
        run_processing_service()

    except KeyboardInterrupt:
        logger.info(
            "IMS Processing Service "
            "stopped by user."
        )

    except Exception:
        logger.exception(
            "IMS Processing Service "
            "terminated due to an "
            "unexpected error."
        )

        raise


if __name__ == "__main__":
    main()
