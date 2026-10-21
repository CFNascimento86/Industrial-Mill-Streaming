from __future__ import annotations
import threading
import time

from datetime import (
    datetime,
    timezone,
)

from acquisition_service.model import (
    AcquisitionReading,
    ReadWindow,
    VariableMapping,
)
from acquisition_service.runtime import (
    run_connected_session,
)


class FakeAcquisitionClient:
    """
    Simula uma fonte industrial e conta
    quantos ciclos foram iniciados.
    """

    def __init__(self):
        self.read_count = 0

    def read_window(
        self,
        window,
    ):
        self.read_count += 1

        return (
            AcquisitionReading(
                logical_name="cane_flow",
                value=float(
                    self.read_count
                ),
                observed_at=datetime.now(
                    timezone.utc
                ),
                quality="UNKNOWN",
            ),
        )


def test_connected_session_waits_for_cycle_processing_before_next_acquisition():
    client = (
        FakeAcquisitionClient()
    )

    window = ReadWindow(
        address=0,
        count=2,
        variables=(
            VariableMapping(
                logical_name="cane_flow",
                address=0,
                data_type="FLOAT32",
            ),
        ),
    )

    stop_event = (
        threading.Event()
    )

    processing_started = (
        threading.Event()
    )

    release_processing = (
        threading.Event()
    )

    second_cycle_started = (
        threading.Event()
    )

    cycle_count = 0

    def on_cycle(
        readings,
    ):
        nonlocal cycle_count

        cycle_count += 1

        if cycle_count == 1:
            processing_started.set()

            # Simula TelemetryPublisher
            # bloqueado aguardando Kafka.
            release_processing.wait(
                timeout=5.0
            )

        elif cycle_count == 2:
            second_cycle_started.set()
            stop_event.set()

    worker = threading.Thread(
        target=run_connected_session,
        kwargs={
            "client": client,
            "windows": (
                window,
            ),
            "expected_readings": 1,
            "poll_interval": 0.01,
            "stop_requested": (
                stop_event.is_set
            ),
            "on_cycle": on_cycle,
        },
        daemon=True,
    )

    worker.start()

    # Primeiro ciclo chegou à etapa
    # de processamento/publicação.
    assert processing_started.wait(
        timeout=2.0
    )

    assert client.read_count == 1

    # Mesmo com poll_interval muito curto,
    # o runtime não pode iniciar nova
    # aquisição enquanto on_cycle bloqueia.
    time.sleep(
        0.2
    )

    assert client.read_count == 1

    assert not (
        second_cycle_started.is_set()
    )

    # Simula recuperação do Kafka e
    # conclusão do batch pendente.
    release_processing.set()

    # Agora o segundo ciclo pode começar.
    assert second_cycle_started.wait(
        timeout=2.0
    )

    assert client.read_count == 2

    worker.join(
        timeout=2.0
    )

    assert not worker.is_alive()
