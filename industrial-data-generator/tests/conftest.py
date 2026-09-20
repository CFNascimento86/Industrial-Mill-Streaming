from __future__ import annotations
from pathlib import Path
import pytest
from config.factory import build_process_engine
from config.loader import (
    load_process_model,
    load_scenarios,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

PROCESS_MODEL_PATH = (
    PROJECT_ROOT
    / "config"
    / "process_model.yaml"
)

SCENARIOS_PATH = (
    PROJECT_ROOT
    / "config"
    / "scenarios.yaml"
)


@pytest.fixture
def process_config():
    """
    Carrega a configuração real da Reference Plant.
    """
    return load_process_model(
        PROCESS_MODEL_PATH
    )


@pytest.fixture
def scenario_config():
    """
    Carrega os cenários reais da Reference Plant.
    """
    return load_scenarios(
        SCENARIOS_PATH
    )


@pytest.fixture
def engine(
    process_config,
    scenario_config,
):
    """
    Cria uma nova instância determinística do ProcessEngine.
    """
    return build_process_engine(
        process_config=process_config,
        scenario_config=scenario_config,
    )
