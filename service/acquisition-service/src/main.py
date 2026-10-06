from __future__ import annotations
import logging
import os
import time
from pathlib import Path
from acquisition_service.client import (
    AcquisitionError,
    ModbusAcquisitionClient,
)
from acquisition_service.mapping import (
    build_read_windows,
    build_variable_mappings,
    load_mapping,
)
from acquisition_service.model import (
    AcquisitionReading,
    ReadWindow,
)
from acquisition_service.runtime import (
    run_reconnecting_loop,
)
from acquisition_service.model import (
    AcquisitionReading,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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

LOG_EVERY_N_CYCLES = 10


def configure_logging() -> None:
    """
    Configura o logging básico do Acquisition Service.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


def get_environment_integer(
    name: str,
    default: int,
) -> int:
    raw_value = os.getenv(
        name,
        str(default),
    )

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable '{name}' "
            "must be an integer."
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
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable '{name}' "
            "must be numeric."
        ) from exc


def run_acquisition_service() -> None:
    """
    Inicializa e executa continuamente
    o IMS Acquisition Service.
    """

    logger = logging.getLogger(
        "ims.acquisition"
    )

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

    modbus_host = os.getenv(
        "MODBUS_HOST",
        DEFAULT_MODBUS_HOST,
    )

    modbus_port = get_environment_integer(
        "MODBUS_PORT",
        DEFAULT_MODBUS_PORT,
    )

    modbus_device_id = get_environment_integer(
        "MODBUS_DEVICE_ID",
        DEFAULT_MODBUS_DEVICE_ID,
    )

    modbus_timeout = get_environment_float(
        "MODBUS_TIMEOUT_SECONDS",
        DEFAULT_MODBUS_TIMEOUT_SECONDS,
    )

    poll_interval = get_environment_float(
        "ACQUISITION_POLL_INTERVAL_SECONDS",
        DEFAULT_POLL_INTERVAL_SECONDS,
    )

    reconnect_interval = get_environment_float(
        "ACQUISITION_RECONNECT_INTERVAL_SECONDS",
        DEFAULT_RECONNECT_INTERVAL_SECONDS,
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

        cycle = 0

    def build_client() -> ModbusAcquisitionClient:
        return ModbusAcquisitionClient(
            host=modbus_host,
            port=modbus_port,
            device_id=modbus_device_id,
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

    def on_cycle(
        readings: tuple[
            AcquisitionReading,
            ...
        ],
    ) -> None:
        nonlocal cycle

        cycle += 1

        if cycle % LOG_EVERY_N_CYCLES != 0:
            return

        readings_by_name = {
            reading.logical_name: reading
            for reading in readings
        }

        logger.info(
            "Cycle=%d | "
            "readings=%d | "
            "windows=%d | "
            "cane_flow=%.2f | "
            "main_drive_01_torque=%.2f | "
            "juice_flow=%.2f | "
            "bagasse_moisture=%.2f",
            cycle,
            len(readings),
            len(windows),
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

    run_reconnecting_loop(
        client_factory=build_client,
        windows=windows,
        expected_readings=len(mappings),
        poll_interval=poll_interval,
        reconnect_interval=reconnect_interval,
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

    except Exception:
        logger.exception(
            "IMS Acquisition Service terminated "
            "due to an unexpected error."
        )

        raise


if __name__ == "__main__":
    main()
