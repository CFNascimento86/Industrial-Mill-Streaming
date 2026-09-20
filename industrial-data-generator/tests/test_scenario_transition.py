from __future__ import annotations
import pytest


def test_high_load_transition_is_progressive(
    engine,
):
    """
    A transição para high_load deve alterar progressivamente o cane_flow.
    """
    scenario_engine = (
        engine.scenario_engine
    )

    assert (
        scenario_engine.get_modifier(
            "cane_flow"
        )
        == pytest.approx(1.0)
    )

    engine.set_scenario(
        "high_load",
        transition_seconds=10.0,
    )

    engine.step(
        dt=5.0
    )

    midpoint = (
        scenario_engine.get_modifier(
            "cane_flow"
        )
    )

    assert 1.0 < midpoint < 1.10

    engine.step(
        dt=5.0
    )

    final = (
        scenario_engine.get_modifier(
            "cane_flow"
        )
    )

    assert final == pytest.approx(
        1.10
    )

    assert not scenario_engine.is_transitioning


def test_process_recovery_returns_modifier_to_nominal(
    engine,
):
    """
    O cenário de recuperação deve retornar progressivamente ao nominal.
    """
    scenario_engine = (
        engine.scenario_engine
    )

    engine.set_scenario(
        "overload",
        transition_seconds=0.0,
    )

    assert (
        scenario_engine.get_modifier(
            "cane_flow"
        )
        == pytest.approx(1.25)
    )

    engine.set_scenario(
        "process_recovery",
        transition_seconds=10.0,
    )

    engine.step(
        dt=5.0
    )

    midpoint = (
        scenario_engine.get_modifier(
            "cane_flow"
        )
    )

    assert 1.0 < midpoint < 1.25

    engine.step(
        dt=5.0
    )

    assert (
        scenario_engine.get_modifier(
            "cane_flow"
        )
        == pytest.approx(1.0)
    )

    assert not scenario_engine.is_transitioning
