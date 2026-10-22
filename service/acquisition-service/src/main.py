from __future__ import annotations
import logging
import os
from pathlib import Path

from acquisition_service.apicurio_wire import (
    ApicurioWireFramer,
)
from acquisition_service.avro_codec import (
    TelemetryAvroCodec,
)
from acquisition_service.client import (
    ModbusAcquisitionClient,
)
from acquisition_service.cycle_processor import (
    TelemetryCycleProcessor,
)
from acquisition_service.kafka_producer import (
    DEFAULT_TELEMETRY_TOPIC,
    KafkaTelemetryProducer,
)
from acquisition_service.mapping import (
    build_read_windows,
    build_variable_mappings,
    load_mapping,
)
from acquisition_service.model import (
    AcquisitionReading,
)
from acquisition_service.postgres_identity import (
    PostgresIdentityResolver,
)
from acquisition_service.registry_client import (
    ApicurioRegistryClient,
)
from acquisition_service.runtime import (
    run_reconnecting_loop,
)
from acquisition_service.telemetry_publisher import (
    TelemetryBatchPublishError,
    TelemetryPublisher,
)
from acquisition_service.transformer import (
    TelemetryTransformer,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MODBUS_MAPPING_PATH = (
    PROJECT_ROOT
    / "config"
    / "modbus_mapping.yaml"
)


DEFAULT_MODBUS_HOST = "127.0.0.1"
DEFAULT_MODBUS_PORT = 1502
DEFAULT_MODBUS_DEVICE_ID = 1
DEFAULT_MODBUS_TIMEOUT_SECONDS = 3.0

DEFAULT_POLL_INTERVAL_SECONDS = 1.0
DEFAULT_RECONNECT_INTERVAL_SECONDS = 5.0

DEFAULT_REGISTRY_URL = (
    "http://localhost:8080/apis/registry/v3"
)

TELEMETRY_SCHEMA_GROUP = (
    "ims.telemetry"
)

TELEMETRY_SCHEMA_ARTIFACT = (
    "telemetry-observation"
)

TELEMETRY_SCHEMA_VERSION = (
    "1.0.0"
)

DEFAULT_KAFKA_BOOTSTRAP_SERVERS = (
    "localhost:9092"
)

DEFAULT_PUBLISH_MAX_ATTEMPTS = 3
DEFAULT_PUBLISH_FLUSH_TIMEOUT_SECONDS = 10.0
DEFAULT_PUBLISH_RETRY_BACKOFF_SECONDS = 1.0

LOG_EVERY_N_CYCLES = 10


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


def get_required_environment(
    name: str,
) -> str:
    value = os.getenv(
        name
    )

    if (
        value is None
        or not value.strip()
    ):
        raise ValueError(
            f"Environment variable "
            f"'{name}' is required."
        )

    return value


def get_environment_integer(
    name: str,
    default: int,
) -> int:
    raw_value = os.getenv(
        name,
        str(default),
    )

    try:
        return int(
            raw_value
        )

    except ValueError as exc:
        raise ValueError(
            f"Environment variable "
            f"'{name}' must be "
            "an integer."
        ) from exc


def get_environment_float(
    name: str,
    default: float,
) -> float:
    raw_value = os.getenv(
        name,
        str(default),
    )

    try:
        return float(
            raw_value
        )

    except ValueError as exc:
        raise ValueError(
            f"Environment variable "
            f"'{name}' must be "
            "numeric."
        ) from exc


def run_acquisition_service() -> None:
    """
    Inicializa e executa continuamente
    o IMS Acquisition Service.
    """

    logger = logging.getLogger(
        "ims.acquisition"
    )

    # ---------------------------------------------------------
    # Acquisition mapping
    # ---------------------------------------------------------

    mapping_config = load_mapping(
        MODBUS_MAPPING_PATH
    )

    mappings = build_variable_mappings(
        mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    encoding = (
        mapping_config[
            "encoding"
        ]["float32"]
    )

    source_name = (
        mapping_config[
            "source"
        ]["logical_name"]
    )

    # ---------------------------------------------------------
    # Runtime configuration
    # ---------------------------------------------------------

    database_url = (
        get_required_environment(
            "DATABASE_URL"
        )
    )

    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        DEFAULT_REGISTRY_URL,
    )

    kafka_bootstrap_servers = (
        os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            DEFAULT_KAFKA_BOOTSTRAP_SERVERS,
        )
    )

    kafka_topic = os.getenv(
        "KAFKA_TELEMETRY_TOPIC",
        DEFAULT_TELEMETRY_TOPIC,
    )

    modbus_host = os.getenv(
        "MODBUS_HOST",
        DEFAULT_MODBUS_HOST,
    )

    modbus_port = (
        get_environment_integer(
            "MODBUS_PORT",
            DEFAULT_MODBUS_PORT,
        )
    )

    modbus_device_id = (
        get_environment_integer(
            "MODBUS_DEVICE_ID",
            DEFAULT_MODBUS_DEVICE_ID,
        )
    )

    modbus_timeout = (
        get_environment_float(
            "MODBUS_TIMEOUT_SECONDS",
            DEFAULT_MODBUS_TIMEOUT_SECONDS,
        )
    )

    poll_interval = (
        get_environment_float(
            "ACQUISITION_POLL_INTERVAL_SECONDS",
            DEFAULT_POLL_INTERVAL_SECONDS,
        )
    )

    reconnect_interval = (
        get_environment_float(
            "ACQUISITION_RECONNECT_INTERVAL_SECONDS",
            DEFAULT_RECONNECT_INTERVAL_SECONDS,
        )
    )

    publish_max_attempts = (
        get_environment_integer(
            "TELEMETRY_PUBLISH_MAX_ATTEMPTS",
            DEFAULT_PUBLISH_MAX_ATTEMPTS,
        )
    )

    publish_flush_timeout = (
        get_environment_float(
            "TELEMETRY_PUBLISH_FLUSH_TIMEOUT_SECONDS",
            DEFAULT_PUBLISH_FLUSH_TIMEOUT_SECONDS,
        )
    )

    publish_retry_backoff = (
        get_environment_float(
            "TELEMETRY_PUBLISH_RETRY_BACKOFF_SECONDS",
            DEFAULT_PUBLISH_RETRY_BACKOFF_SECONDS,
        )
    )

    if poll_interval <= 0:
        raise ValueError(
            "ACQUISITION_POLL_INTERVAL_SECONDS "
            "must be greater than zero."
        )

    if reconnect_interval < 0:
        raise ValueError(
            "ACQUISITION_RECONNECT_INTERVAL_SECONDS "
            "cannot be negative."
        )

    if modbus_timeout <= 0:
        raise ValueError(
            "MODBUS_TIMEOUT_SECONDS "
            "must be greater than zero."
        )

    if publish_max_attempts < 1:
        raise ValueError(
            "TELEMETRY_PUBLISH_MAX_ATTEMPTS "
            "must be >= 1."
        )

    if publish_flush_timeout <= 0:
        raise ValueError(
            "TELEMETRY_PUBLISH_FLUSH_TIMEOUT_SECONDS "
            "must be greater than zero."
        )

    if publish_retry_backoff < 0:
        raise ValueError(
            "TELEMETRY_PUBLISH_RETRY_BACKOFF_SECONDS "
            "cannot be negative."
        )

    # ---------------------------------------------------------
    # Industrial identity
    #
    # Control plane:
    # PostgreSQL is consulted once at startup.
    # ---------------------------------------------------------

    identity_resolver = (
        PostgresIdentityResolver
        .from_database(
            database_url=database_url,
            source_logical_name=(
                source_name
            ),
        )
    )

    # ---------------------------------------------------------
    # Governed telemetry contract
    #
    # Control plane:
    # Apicurio is consulted once at startup.
    # ---------------------------------------------------------

    registry_client = (
        ApicurioRegistryClient(
            registry_url,
            timeout=5.0,
        )
    )

    registered_schema = (
        registry_client
        .resolve_avro_schema(
            group_id=(
                TELEMETRY_SCHEMA_GROUP
            ),
            artifact_id=(
                TELEMETRY_SCHEMA_ARTIFACT
            ),
            version=(
                TELEMETRY_SCHEMA_VERSION
            ),
        )
    )

    codec = TelemetryAvroCodec(
        registered_schema.schema
    )

    framer = ApicurioWireFramer(
        content_id=(
            registered_schema.content_id
        )
    )

    # ---------------------------------------------------------
    # Kafka transport
    # ---------------------------------------------------------

    kafka_transport = (
        KafkaTelemetryProducer(
            bootstrap_servers=(
                kafka_bootstrap_servers
            ),
            topic=kafka_topic,
        )
    )

    telemetry_publisher = (
        TelemetryPublisher(
            codec=codec,
            framer=framer,
            transport=kafka_transport,
            max_attempts=(
                publish_max_attempts
            ),
            flush_timeout=(
                publish_flush_timeout
            ),
            retry_backoff_seconds=(
                publish_retry_backoff
            ),
        )
    )

    # ---------------------------------------------------------
    # Industrial transformation
    # ---------------------------------------------------------

    transformer = (
        TelemetryTransformer(
            identity_resolver=(
                identity_resolver
            ),
            source_logical_name=(
                source_name
            ),
        )
    )

    cycle_processor = (
        TelemetryCycleProcessor(
            transformer=transformer,
            publisher=(
                telemetry_publisher
            ),
        )
    )

    # ---------------------------------------------------------
    # Startup state
    # ---------------------------------------------------------

    logger.info(
        "IMS Acquisition Service initialized."
    )

    logger.info(
        "Source=%s | "
        "Modbus=%s:%d | "
        "Device ID=%d | "
        "Variables=%d | "
        "Read windows=%d | "
        "Poll interval=%.3f s",
        source_name,
        modbus_host,
        modbus_port,
        modbus_device_id,
        len(mappings),
        len(windows),
        poll_interval,
    )

    logger.info(
        "Telemetry contract="
        "%s/%s:%s | "
        "contentId=%d | "
        "state=%s",
        registered_schema.group_id,
        registered_schema.artifact_id,
        registered_schema.version,
        registered_schema.content_id,
        registered_schema.state,
    )

    logger.info(
        "Kafka=%s | "
        "Topic=%s",
        kafka_bootstrap_servers,
        kafka_topic,
    )

    cycle = 0

    # ---------------------------------------------------------
    # Modbus factory
    # ---------------------------------------------------------

    def build_client(
    ) -> ModbusAcquisitionClient:
        return ModbusAcquisitionClient(
            host=modbus_host,
            port=modbus_port,
            device_id=(
                modbus_device_id
            ),
            byte_order=encoding[
                "byte_order"
            ],
            word_order=encoding[
                "word_order"
            ],
            timeout=modbus_timeout,
        )

    def on_connected() -> None:
        logger.info(
            "Connected to Modbus source "
            "%s:%d.",
            modbus_host,
            modbus_port,
        )

    # ---------------------------------------------------------
    # Runtime barrier
    #
    # Esta função somente retorna quando
    # o batch foi concluído pelo publisher.
    # ---------------------------------------------------------

    def on_cycle(
        readings: tuple[
            AcquisitionReading,
            ...
        ],
    ) -> None:
        nonlocal cycle

        observations = (
            cycle_processor.process(
                readings
            )
        )

        cycle += 1

        if (
            cycle
            % LOG_EVERY_N_CYCLES
            != 0
        ):
            return

        readings_by_name = {
            reading.logical_name:
                reading
            for reading in readings
        }

        logger.info(
            "Cycle=%d | "
            "readings=%d | "
            "observations=%d | "
            "published=%d | "
            "cane_flow=%.2f | "
            "main_drive_01_torque=%.2f | "
            "juice_flow=%.2f | "
            "bagasse_moisture=%.2f",
            cycle,
            len(readings),
            len(observations),
            len(observations),
            readings_by_name[
                "cane_flow"
            ].value,
            readings_by_name[
                "main_drive_01_torque"
            ].value,
            readings_by_name[
                "juice_flow"
            ].value,
            readings_by_name[
                "bagasse_moisture"
            ].value,
        )

    # ---------------------------------------------------------
    # Continuous runtime
    # ---------------------------------------------------------

    run_reconnecting_loop(
        client_factory=build_client,
        windows=windows,
        expected_readings=len(
            mappings
        ),
        poll_interval=poll_interval,
        reconnect_interval=(
            reconnect_interval
        ),
        stop_requested=lambda: False,
        on_connected=on_connected,
        on_cycle=on_cycle,
    )


def main() -> None:
    configure_logging()

    logger = logging.getLogger(
        "ims.acquisition"
    )

    try:
        run_acquisition_service()

    except KeyboardInterrupt:
        logger.info(
            "IMS Acquisition Service "
            "stopped by user."
        )

    except TelemetryBatchPublishError:
        logger.exception(
            "IMS Acquisition Service stopped "
            "because a telemetry batch could "
            "not be delivered."
        )

        raise

    except Exception:
        logger.exception(
            "IMS Acquisition Service terminated "
            "due to an unexpected error."
        )

        raise


if __name__ == "__main__":
    main()
