from __future__ import annotations
from copy import deepcopy
from config.factory import build_process_engine


def test_signal_order_does_not_change_results(
    process_config,
    scenario_config,
):
    """
    A ordem declarativa dos sinais não deve alterar a dinâmica simulada.
    Cada variável possui PRNG determinístico próprio e todos os modelos
    utilizam o mesmo State(t) durante cada ciclo.
    """
    original_config = deepcopy(
        process_config
    )

    reversed_config = deepcopy(
        process_config
    )

    reversed_config["signals"] = list(
        reversed(
            reversed_config["signals"]
        )
    )

    engine_a = build_process_engine(
        process_config=original_config,
        scenario_config=scenario_config,
    )

    engine_b = build_process_engine(
        process_config=reversed_config,
        scenario_config=scenario_config,
    )

    for _ in range(60):
        snapshot_a = engine_a.step(
            dt=1.0
        )

        snapshot_b = engine_b.step(
            dt=1.0
        )

        assert snapshot_a == snapshot_b
