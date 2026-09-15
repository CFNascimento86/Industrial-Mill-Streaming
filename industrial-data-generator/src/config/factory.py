from __future__ import annotations
from random import Random
from typing import Any
from process.engine import ProcessEngine, SignalDefinition
from process.state import ProcessState
from scenarios.engine import (
    ScenarioDefinition,
    ScenarioEffect,
    ScenarioEngine,
)
from signals.base import SignalModel
from signals.bounded_variation import (
    BoundedVariationConfig,
    BoundedVariationModel,
)
from signals.load_correlated import (
    LoadCorrelatedConfig,
    LoadCorrelatedModel,
)
from signals.process_correlated import (
    ProcessCorrelatedConfig,
    ProcessCorrelatedModel,
)
from signals.process_driver import (
    ProcessDriverConfig,
    ProcessDriverModel,
)
from signals.slow_thermal import (
    SlowThermalConfig,
    SlowThermalModel,
)

from .loader import ConfigurationError


def build_process_engine(
    *,
    process_config: dict[str, Any],
    scenario_config: dict[str, Any],
) -> ProcessEngine:
    """
    Constrói um ProcessEngine completamente configurado.
    A factory resolve:
        - estado inicial;
        - baselines;
        - modelos de sinais;
        - dependências entre sinais;
        - cenários;
        - modificadores;
        - seed determinístico.
    """

    simulation = process_config["simulation"]

    random_seed = simulation["random_seed"]

    random_generator = Random(
        random_seed
    )

    baselines = _extract_baselines(
        process_config
    )

    state = _build_process_state(
        baselines
    )

    signal_definitions = _build_signal_definitions(
        process_config=process_config,
        baselines=baselines,
        random_generator=random_generator,
    )

    scenario_engine = _build_scenario_engine(
        scenario_config=scenario_config,
    )

    return ProcessEngine(
        state=state,
        scenario_engine=scenario_engine,
        signals=signal_definitions,
    )
