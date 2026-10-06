from __future__ import annotations
import logging
import time
from collections.abc import Callable
from acquisition_service.client import (
    AcquisitionError,
    ModbusAcquisitionClient,
)
from acquisition_service.model import (
    AcquisitionReading,
    ReadWindow,
)


LOGGER = logging.getLogger("ims.acquisition")


def acquire_cycle(
    *,
    client: ModbusAcquisitionClient,
    windows: tuple[ReadWindow, ...],
) -> tuple[AcquisitionReading, ...]:
    """
    Executa um ciclo completo de aquisição.
    """

    readings: list[AcquisitionReading] = []

    for window in windows:
        readings.extend(
            client.read_window(window)
        )

    return tuple(readings)


def validate_cycle(
    *,
    readings: tuple[AcquisitionReading, ...],
    expected_count: int,
) -> None:
    """
    Valida a completude estrutural do ciclo.
    """

    if len(readings) != expected_count:
        raise AcquisitionError(
            "Incomplete acquisition cycle: "
            f"expected {expected_count} readings, "
            f"received {len(readings)}."
        )

    logical_names = {
        reading.logical_name
        for reading in readings
    }

    if len(logical_names) != expected_count:
        raise AcquisitionError(
            "Acquisition cycle contains "
            "duplicated logical names."
        )


def run_connected_session(
    *,
    client: ModbusAcquisitionClient,
    windows: tuple[ReadWindow, ...],
    expected_readings: int,
    poll_interval: float,
    stop_requested: Callable[[], bool],
    on_cycle: (
        Callable[
            [tuple[AcquisitionReading, ...]],
            None,
        ]
        | None
    ) = None,
) -> None:
    """
    Executa ciclos enquanto a conexão permanecer saudável.
    """

    next_cycle_time = time.monotonic()

    while not stop_requested():
        readings = acquire_cycle(
            client=client,
            windows=windows,
        )

        validate_cycle(
            readings=readings,
            expected_count=expected_readings,
        )

        if on_cycle is not None:
            on_cycle(readings)

        next_cycle_time += poll_interval

        sleep_seconds = (
            next_cycle_time
            - time.monotonic()
        )

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
        else:
            next_cycle_time = time.monotonic()


def _interruptible_sleep(
    *,
    duration: float,
    stop_requested: Callable[[], bool],
) -> None:
    """
    Permite interromper rapidamente o período de reconexão.
    """

    deadline = (
        time.monotonic()
        + duration
    )

    while not stop_requested():
        remaining = (
            deadline
            - time.monotonic()
        )

        if remaining <= 0:
            return

        time.sleep(
            min(
                remaining,
                0.1,
            )
        )


def run_reconnecting_loop(
    *,
    client_factory: Callable[
        [],
        ModbusAcquisitionClient,
    ],
    windows: tuple[ReadWindow, ...],
    expected_readings: int,
    poll_interval: float,
    reconnect_interval: float,
    stop_requested: Callable[[], bool],
    on_connected: Callable[[], None] | None = None,
    on_cycle: (
        Callable[
            [tuple[AcquisitionReading, ...]],
            None,
        ]
        | None
    ) = None,
    on_interrupted: (
        Callable[[AcquisitionError], None]
        | None
    ) = None,
) -> None:
    """
    Coordena conexão, aquisição, falha e reconexão.
    """

    while not stop_requested():
        client = client_factory()

        try:
            client.connect()

            if on_connected is not None:
                on_connected()

            run_connected_session(
                client=client,
                windows=windows,
                expected_readings=expected_readings,
                poll_interval=poll_interval,
                stop_requested=stop_requested,
                on_cycle=on_cycle,
            )

        except AcquisitionError as exc:
            if on_interrupted is not None:
                on_interrupted(exc)

            LOGGER.warning(
                "Acquisition interrupted: %s",
                exc,
            )

        finally:
            client.close()

        if stop_requested():
            return

        LOGGER.info(
            "Reconnecting in %.1f seconds.",
            reconnect_interval,
        )

        _interruptible_sleep(
            duration=reconnect_interval,
            stop_requested=stop_requested,
        )
