from __future__ import annotations
from statistics import mean


def _collect_values(
    engine,
    *,
    signal: str,
    cycles: int,
) -> list[float]:
    """
    Coleta valores consecutivos de uma variável.
    """
    values: list[float] = []

    for _ in range(cycles):
        snapshot = engine.step(
            dt=1.0
        )

        values.append(
            snapshot[signal]
        )

    return values


def test_torque_increases_under_sustained_high_load(
    engine,
):
    """
    Carga elevada sustentada deve elevar o torque médio.
    """
    nominal_values = _collect_values(
        engine,
        signal="main_drive_01_torque",
        cycles=60,
    )

    nominal_average = mean(
        nominal_values[-30:]
    )

    engine.set_scenario(
        "high_load",
        transition_seconds=0.0,
    )

    high_load_values = _collect_values(
        engine,
        signal="main_drive_01_torque",
        cycles=60,
    )

    high_load_average = mean(
        high_load_values[-30:]
    )

    assert (
        high_load_average
        > nominal_average
    )


def test_torque_decreases_under_low_feed(
    engine,
):
    """
    Baixa alimentação sustentada deve reduzir o torque médio.
    """
    nominal_values = _collect_values(
        engine,
        signal="main_drive_01_torque",
        cycles=60,
    )

    nominal_average = mean(
        nominal_values[-30:]
    )

    engine.set_scenario(
        "low_feed",
        transition_seconds=0.0,
    )

    low_feed_values = _collect_values(
        engine,
        signal="main_drive_01_torque",
        cycles=60,
    )

    low_feed_average = mean(
        low_feed_values[-30:]
    )

    assert (
        low_feed_average
        < nominal_average
    )


def test_juice_flow_follows_cane_flow_trend(
    engine,
):
    """
    Juice flow deve responder positivamente à elevação sustentada de cane flow.
    """
    nominal_values = _collect_values(
        engine,
        signal="juice_flow",
        cycles=60,
    )

    nominal_average = mean(
        nominal_values[-30:]
    )

    engine.set_scenario(
        "high_load",
        transition_seconds=0.0,
    )

    high_load_values = _collect_values(
        engine,
        signal="juice_flow",
        cycles=60,
    )

    high_load_average = mean(
        high_load_values[-30:]
    )

    assert (
        high_load_average
        > nominal_average
    )
