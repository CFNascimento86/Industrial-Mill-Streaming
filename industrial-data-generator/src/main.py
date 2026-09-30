from __future__ import annotations
import asyncio
import logging
import os
from pathlib import Path
from typing import Any
from config.factory import build_process_engine
from config.loader import (
    load_process_model,
    load_reference_modbus_model,
    load_scenarios,
)
from modbus.factory import build_modbus_reference_model
from modbus.runtime import ModbusRuntime
from modbus.server import PyModbusServerAdapter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"

PROCESS_MODEL_PATH = (
    CONFIG_DIR
    / "process_model.yaml"
)

SCENARIOS_PATH = (
    CONFIG_DIR
    / "scenarios.yaml"
)

REFERENCE_MODBUS_MODEL_PATH = (
    CONFIG_DIR
    / "reference_modbus_model.yaml"
)


DEFAULT_MODBUS_HOST = "0.0.0.0"
DEFAULT_MODBUS_PORT = 1502
DEFAULT_MODBUS_DEVICE_ID = 1

LOG_EVERY_N_CYCLES = 10


def configure_logging() -> None:
    """
    Configura logging básico do Industrial Data Generator.
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


def load_configuration() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """
    Carrega as configurações necessárias ao runtime.
    """

    process_config = load_process_model(
        PROCESS_MODEL_PATH
    )

    scenario_config = load_scenarios(
        SCENARIOS_PATH
    )

    modbus_config = load_reference_modbus_model(
        REFERENCE_MODBUS_MODEL_PATH
    )

    return (
        process_config,
        scenario_config,
        modbus_config,
    )


def get_update_interval(
    process_config: dict[str, Any],
) -> float:
    """
    Obtém e valida o intervalo de atualização do processo.
    """

    try:
        update_interval = float(
            process_config["simulation"][
                "update_interval_seconds"
            ]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "'simulation.update_interval_seconds' "
            "must be a numeric value."
        ) from exc

    if update_interval <= 0:
        raise ValueError(
            "'simulation.update_interval_seconds' "
            "must be greater than zero."
        )

    return update_interval


def get_environment_integer(
    name: str,
    default: int,
) -> int:
    """
    Obtém uma variável de ambiente inteira.
    """

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


async def run_reference_plant() -> None:
    """
    Executa continuamente a IMS Reference Plant.
    """

    logger = logging.getLogger(
        "ims.reference_plant"
    )

    (
        process_config,
        scenario_config,
        modbus_config,
    ) = load_configuration()

    process_engine = build_process_engine(
        process_config=process_config,
        scenario_config=scenario_config,
    )

    modbus_model = build_modbus_reference_model(
        modbus_config
    )

    modbus_runtime = ModbusRuntime(
        modbus_model
    )

    update_interval = get_update_interval(
        process_config
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

    modbus_server = PyModbusServerAdapter(
        runtime=modbus_runtime,
        host=modbus_host,
        port=modbus_port,
        device_id=modbus_device_id,
    )

    # Materializa o estado inicial sem avançar o processo.
    initial_snapshot = process_engine.snapshot()

    modbus_runtime.write_snapshot(
        initial_snapshot
    )

    await modbus_server.start()

    await modbus_server.sync_from_runtime()

    logger.info(
        "IMS Reference Plant initialized."
    )

    logger.info(
        "Process: %s | Registers: %d | "
        "Update interval: %.3f s | "
        "Modbus TCP: %s:%d | Device ID: %d",
        modbus_model.process,
        modbus_runtime.size,
        update_interval,
        modbus_host,
        modbus_port,
        modbus_device_id,
    )

    cycle = 0

    event_loop = asyncio.get_running_loop()
    next_cycle_time = event_loop.time()

    try:
        while True:
            snapshot = process_engine.step(
                dt=update_interval
            )

            modbus_runtime.write_snapshot(
                snapshot
            )

            await modbus_server.sync_from_runtime()

            cycle += 1

            if cycle % LOG_EVERY_N_CYCLES == 0:
                logger.info(
                    "Cycle=%d | "
                    "cane_flow=%.2f | "
                    "main_drive_01_torque=%.2f | "
                    "juice_flow=%.2f | "
                    "bagasse_moisture=%.2f",
                    cycle,
                    snapshot["cane_flow"],
                    snapshot[
                        "main_drive_01_torque"
                    ],
                    snapshot["juice_flow"],
                    snapshot[
                        "bagasse_moisture"
                    ],
                )

            next_cycle_time += update_interval

            sleep_seconds = (
                next_cycle_time
                - event_loop.time()
            )

            if sleep_seconds > 0:
                await asyncio.sleep(
                    sleep_seconds
                )
            else:
                next_cycle_time = (
                    event_loop.time()
                )

    finally:
        await modbus_server.stop()


def main() -> None:
    configure_logging()

    try:
        asyncio.run(
            run_reference_plant()
        )
    except KeyboardInterrupt:
        logging.getLogger(
            "ims.reference_plant"
        ).info(
            "IMS Reference Plant stopped by user."
        )


if __name__ == "__main__":
    main()
