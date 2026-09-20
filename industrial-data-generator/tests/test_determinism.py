from __future__ import annotations
from copy import deepcopy
from config.factory import build_process_engine


def test_same_seed_produces_same_sequence(
    process_config,
    scenario_config,
):
    """
    Mesma configuração e mesma seed devem produzir a mesma sequência.
    """
    engine_a = build_process_engine(
        process_config=process_config,
        scenario_config=scenario_config,
    )

    engine_b = build_process_engine(
        process_config=process_config,
        scenario_config=scenario_config,
    )

    sequence_a = [
        engine_a.step(dt=1.0)
        for _ in range(60)
    ]

    sequence_b = [
        engine_b.step(dt=1.0)
        for _ in range(60)
    ]

    assert sequence_a == sequence_b


def test_different_seed_produces_different_sequence(
    process_config,
    scenario_config,
):
    """
    Seeds diferentes devem produzir variações sintéticas diferentes.
    """
    config_a = deepcopy(
        process_config
    )

    config_b = deepcopy(
        process_config
    )

    config_a["simulation"][
        "random_seed"
    ] = 42

    config_b["simulation"][
        "random_seed"
    ] = 99

    engine_a = build_process_engine(
        process_config=config_a,
        scenario_config=scenario_config,
    )

    engine_b = build_process_engine(
        process_config=config_b,
        scenario_config=scenario_config,
    )

    sequence_a = [
        engine_a.step(dt=1.0)
        for _ in range(30)
    ]

    sequence_b = [
        engine_b.step(dt=1.0)
        for _ in range(30)
    ]

    assert sequence_a != sequence_b
