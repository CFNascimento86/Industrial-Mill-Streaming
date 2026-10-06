from __future__ import annotations
import os
import socket
import subprocess
import threading
import time
import pytest
from acquisition_service.client import (
    ModbusAcquisitionClient,
)
from acquisition_service.mapping import (
    build_read_windows,
    build_variable_mappings,
)
from acquisition_service.runtime import (
    run_reconnecting_loop,
)


RUN_RECOVERY_TESTS = (
    os.getenv(
        "RUN_RECOVERY_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_RECOVERY_TESTS,
        reason=(
            "Recovery integration test requires "
            "RUN_RECOVERY_INTEGRATION_TESTS=1."
        ),
    ),
]


CONTAINER_NAME = (
    "ims-reference-plant-recovery-test"
)

REFERENCE_PLANT_IMAGE = os.getenv(
    "REFERENCE_PLANT_IMAGE",
    "ims-industrial-data-generator:0.1.0",
)

HOST = "127.0.0.1"

HOST_PORT = int(
    os.getenv(
        "RECOVERY_TEST_PORT",
        "1503",
    )
)

CONTAINER_PORT = 1502

DEVICE_ID = 1


def _docker(
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "docker",
            *args,
        ],
        check=check,
        capture_output=True,
        text=True,
    )


def _start_reference_plant() -> None:
    _docker(
        "rm",
        "-f",
        CONTAINER_NAME,
        check=False,
    )

    _docker(
        "run",
        "-d",
        "--rm",
        "--name",
        CONTAINER_NAME,
        "-p",
        (
            f"{HOST_PORT}:"
            f"{CONTAINER_PORT}"
        ),
        REFERENCE_PLANT_IMAGE,
    )


def _stop_reference_plant() -> None:
    _docker(
        "stop",
        CONTAINER_NAME,
        check=False,
    )


def _port_is_open() -> bool:
    try:
        with socket.create_connection(
            (
                HOST,
                HOST_PORT,
            ),
            timeout=0.5,
        ):
            return True

    except OSError:
        return False


def _wait_until(
    condition,
    *,
    timeout: float = 15.0,
) -> None:
    deadline = (
        time.monotonic()
        + timeout
    )

    while (
        time.monotonic()
        < deadline
    ):
        if condition():
            return

        time.sleep(0.1)

    raise AssertionError(
        "Condition was not satisfied "
        f"within {timeout} seconds."
    )


def test_acquisition_recovers_after_source_restart(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    encoding = (
        modbus_mapping_config[
            "encoding"
        ]["float32"]
    )

    stop_event = threading.Event()

    connections: list[float] = []
    cycles: list[object] = []
    interruptions: list[Exception] = []
    unexpected_errors: list[Exception] = []

    def build_client() -> ModbusAcquisitionClient:
        return ModbusAcquisitionClient(
            host=HOST,
            port=HOST_PORT,
            device_id=DEVICE_ID,
            byte_order=encoding[
                "byte_order"
            ],
            word_order=encoding[
                "word_order"
            ],
            timeout=1.0,
        )

    def target() -> None:
        try:
            run_reconnecting_loop(
                client_factory=build_client,
                windows=windows,
                expected_readings=len(
                    mappings
                ),
                poll_interval=0.25,
                reconnect_interval=0.5,
                stop_requested=(
                    stop_event.is_set
                ),
                on_connected=lambda: (
                    connections.append(
                        time.monotonic()
                    )
                ),
                on_cycle=lambda readings: (
                    cycles.append(
                        readings
                    )
                ),
                on_interrupted=lambda exc: (
                    interruptions.append(
                        exc
                    )
                ),
            )

        except Exception as exc:
            unexpected_errors.append(
                exc
            )

            stop_event.set()

    try:
        # -----------------------------------------------------
        # Initial source
        # -----------------------------------------------------

        _start_reference_plant()

        _wait_until(
            _port_is_open
        )

        worker = threading.Thread(
            target=target,
            daemon=True,
        )

        worker.start()

        _wait_until(
            lambda: len(cycles) >= 1
        )

        assert len(connections) >= 1

        cycles_before_failure = len(
            cycles
        )

        # -----------------------------------------------------
        # Source failure
        # -----------------------------------------------------

        _stop_reference_plant()

        _wait_until(
            lambda: (
                len(interruptions)
                >= 1
            )
        )

        assert not unexpected_errors

        # -----------------------------------------------------
        # Source recovery
        # -----------------------------------------------------

        _start_reference_plant()

        _wait_until(
            lambda: len(connections) >= 2
        )

        _wait_until(
            lambda: (
                len(cycles)
                > cycles_before_failure
            )
        )

        assert not unexpected_errors

        latest_cycle = cycles[-1]

        assert len(latest_cycle) == 19

        assert {
            reading.logical_name
            for reading in latest_cycle
        } == {
            mapping.logical_name
            for mapping in mappings
        }

    finally:
        stop_event.set()

        _stop_reference_plant()

        if "worker" in locals():
            worker.join(
                timeout=5.0
            )
