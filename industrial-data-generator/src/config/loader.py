from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml


class ConfigurationError(ValueError):
    """
    Erro relacionado à configuração do Industrial Data Generator.
    """


def load_yaml(path: str | Path) -> dict[str, Any]:
    """
    Carrega um arquivo YAML e retorna sua estrutura como dicionário.
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Configuration file '{file_path}' was not found."
        )

    if not file_path.is_file():
        raise ConfigurationError(
            f"Configuration path '{file_path}' is not a file."
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ConfigurationError(
            f"Configuration file '{file_path}' "
            "must contain a YAML mapping at its root."
        )

    return data


def load_process_model(
    path: str | Path,
) -> dict[str, Any]:
    """
    Carrega e valida a estrutura básica do process_model.yaml.
    """

    data = load_yaml(path)

    _require_sections(
        data=data,
        required_sections={
            "model",
            "simulation",
            "signals",
        },
        source="process model", 
        
    
    if not isinstance(
        data["simulation"],
        dict,
    ):
        raise ConfigurationError(
            "'simulation' in process model must be a mapping."
        )

    if not isinstance(
        data["signals"],
        list,
    ):
        raise ConfigurationError(
            "'signals' in process model must be a list."
        )

    if not data["signals"]:
        raise ConfigurationError(
            "Process model must define at least one signal."
        )

    return data


def load_scenarios(
    path: str | Path,
) -> dict[str, Any]:
    """
    Carrega e valida a estrutura básica do scenarios.yaml.
    """

    data = load_yaml(path)

     _require_sections(
        data=data,
        required_sections={
            "scenario_model",
            "modifiers",
            "scenarios",
        },
        source="scenario model",
    )

    if not isinstance(
        data["scenario_model"],
        dict,
    ):
        raise ConfigurationError(
            "'scenario_model' must be a mapping."
        )

    if not isinstance(
        data["modifiers"],
        dict,
    ):
        raise ConfigurationError(
            "'modifiers' in scenario model must be a mapping."
        )

    if not isinstance(
        data["scenarios"],
        dict,
    ):
        raise ConfigurationError(
            "'scenarios' in scenario model must be a mapping."
        )

    if not data["scenarios"]:
        raise ConfigurationError(
            "Scenario model must define at least one scenario."
        )

    return data


def load_reference_s7_model(
    path: str | Path,
) -> dict[str, Any]:
    """
    Carrega e valida a estrutura básica do reference_s7_model.yaml.
    """

    data = load_yaml(
        path
    )

    _require_sections(
        data=data,
        required_sections={
            "model",
            "data_blocks",
        },
        source="reference S7 model",
    )

    if not isinstance(
        data["model"],
        dict,
    ):
        raise ConfigurationError(
            "'model' in reference S7 model must be a mapping."
        )

    if not isinstance(
        data["data_blocks"],
        list,
    ):
        raise ConfigurationError(
            "'data_blocks' in reference S7 model must be a list."
        )

    if not data["data_blocks"]:
        raise ConfigurationError(
            "Reference S7 model must define at least one data block."
        )

    return data


def _require_sections(
    *,
    data: dict[str, Any],
    required_sections: set[str],
    source: str,
) -> None:
    """
    Verifica a presença das seções obrigatórias de uma configuração.
    """

    missing = (
        required_sections
        - set(data)
    )

    if missing:
        missing_sections = ", ".join(
            sorted(missing)
        )

        raise ConfigurationError(
            f"Missing required sections in {source}: "
            f"{missing_sections}"
        )
