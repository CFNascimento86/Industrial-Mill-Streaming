from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Any
from config.factory import build_process_engine
from config.loader import (
    load_process,
    load_reference_modbus_model,
    load_scenarios,
)
from modbus.factory import build_modbus_reference_model
from modbus.runtime import ModbusRuntime


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"

PROCESS_MODEL_PATH = CONFIG_DIR / "process.yaml"
SCENARIOS_PATH = CONFIG_DIR / "scenarios.yaml"
REFERENCE_MODBUS_MODEL_PATH = (
    CONFIG_DIR / "reference_modbus_model.yaml"
)

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

    process_config = load_process(
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


def run_reference_plant() -> None:
    """
    Executa continuamente a IMS Reference Plant.

    Fluxo:

        ProcessEngine
            ↓
        Industrial Snapshot
            ↓
        ModbusRuntime
            ↓
        Holding Register Map
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

    logger.info(
        "IMS Reference Plant initialized."
    )

    logger.info(
        "Process: %s | Modbus registers: %d | "
        "Update interval: %.3f s",
        modbus_model.process,
        modbus_runtime.size,
        update_interval,
    )

    cycle = 0
    next_cycle_time = time.monotonic()

    try:
        while True:
            snapshot = process_engine.step(
                dt=update_interval
            )

            modbus_runtime.write_snapshot(
                snapshot
            )

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

            # Mantém cadência baseada em relógio monotônico,
            # evitando influência de alterações no relógio do SO.
            next_cycle_time += update_interval

            sleep_seconds = (
                next_cycle_time
                - time.monotonic()
            )

            if sleep_seconds > 0:
                time.sleep(
                    sleep_seconds
                )
            else:
                # Se o processamento ultrapassar o período,
                # reinicia a referência temporal do próximo ciclo.
                next_cycle_time = time.monotonic()

    except KeyboardInterrupt:
        logger.info(
            "IMS Reference Plant stopped by user."
        )


def main() -> None:
    configure_logging()
    run_reference_plant()


if __name__ == "__main__":
    main()
