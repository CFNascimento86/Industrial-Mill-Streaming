from __future__ import annotations
import hashlib
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
    """

    simulation = process_config["simulation"]

    try:
        base_seed = int(
            simulation["random_seed"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(
            "'simulation.random_seed' must be an integer."
        ) from exc

    baselines = _extract_baselines(
        process_config
    )

    state = _build_process_state(
        baselines
    )

    signal_definitions = _build_signal_definitions(
        process_config=process_config,
        baselines=baselines,
        base_seed=base_seed,
    )

    scenario_engine = _build_scenario_engine(
        default_scenario = process_config["simulation"]["default_scenario"]
        known_signals=set(baselines),
    )

    return ProcessEngine(
        state=state,
        scenario_engine=scenario_engine,
        signals=signal_definitions,
    )


def _extract_baselines(
    process_config: dict[str, Any],
) -> dict[str, float]:
    """
    Extrai e valida os baselines das variáveis.
    """

    baselines: dict[str, float] = {}

    for signal in process_config["signals"]:
        try:
            logical_name = signal["variable"]
            baseline = float(
                signal["baseline"]
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ConfigurationError(
                "Every signal must define a valid "
                "'variable' and numeric 'baseline'."
            ) from exc

        if logical_name in baselines:
            raise ConfigurationError(
                f"Signal '{logical_name}' is defined more than once."
            )

        if baseline <= 0:
            raise ConfigurationError(
                f"Baseline for signal '{logical_name}' "
                "must be greater than zero."
            )

        baselines[logical_name] = baseline

    return baselines


def _build_process_state(
    baselines: dict[str, float],
) -> ProcessState:
    """
    Inicializa o processo em suas condições nominais.
    """

    state = ProcessState()

    for logical_name, baseline in baselines.items():
        state.register_signal(
            logical_name=logical_name,
            initial_value=baseline,
        )

    return state


def _build_signal_definitions(
    *,
    process_config: dict[str, Any],
    baselines: dict[str, float],
    base_seed: int,
) -> dict[str, SignalDefinition]:
    """
    Constrói todas as definições executáveis de sinais.
    """

    definitions: dict[
        str,
        SignalDefinition,
    ] = {}

    for signal_config in process_config["signals"]:
        logical_name = signal_config[
            "variable"
        ]

        baseline = baselines[
            logical_name
        ]

        random_generator = _build_signal_random(
            base_seed=base_seed,
            logical_name=logical_name,
        )

        model = _build_signal_model(
            logical_name=logical_name,
            signal_config=signal_config,
            baselines=baselines,
            random_generator=random_generator,
        )

        definitions[logical_name] = SignalDefinition(
            baseline=baseline,
            model=model,
        )

    return definitions


def _build_signal_random(
    *,
    base_seed: int,
    logical_name: str,
) -> Random:
    """
    Cria um PRNG determinístico e independente para cada variável.
    Isso impede que a ordem de declaração dos sinais altere a sequência
    pseudoaleatória associada a cada modelo.
    """

    material = (
        f"{base_seed}:{logical_name}"
        .encode("utf-8")
    )

    digest = hashlib.sha256(
        material
    ).digest()

    signal_seed = int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=False,
    )

    return Random(
        signal_seed
    )


def _build_signal_model(
    *,
    logical_name: str,
    signal_config: dict[str, Any],
    baselines: dict[str, float],
    random_generator: Random,
) -> SignalModel:
    """
    Constrói o modelo associado a uma variável.
    """

    try:
        model_name = signal_config[
            "model"
        ]
    except KeyError as exc:
        raise ConfigurationError(
            f"Signal '{logical_name}' does not define a model."
        ) from exc

    raw_parameters = signal_config.get(
        "parameters",
        {}
    )

    if not isinstance(
        raw_parameters,
        dict,
    ):
        raise ConfigurationError(
            f"Parameters for signal '{logical_name}' "
            "must be a mapping."
        )

    parameters = dict(
        raw_parameters
    )

    try:
        if model_name == "bounded_variation":
            return BoundedVariationModel(
                random_generator=random_generator,
                config=BoundedVariationConfig(
                    **parameters
                ),
            )

        if model_name == "process_driver":
            return ProcessDriverModel(
                random_generator=random_generator,
                config=ProcessDriverConfig(
                    **parameters
                ),
            )

        if model_name == "load_correlated":
            driver_signal = _resolve_driver(
                logical_name=logical_name,
                parameters=parameters,
                baselines=baselines,
            )

            return LoadCorrelatedModel(
                random_generator=random_generator,
                config=LoadCorrelatedConfig(
                    driver_signal=driver_signal,
                    driver_baseline=baselines[
                        driver_signal
                    ],
                    **parameters,
                ),
            )

        if model_name == "process_correlated":
            driver_signal = _resolve_driver(
                logical_name=logical_name,
                parameters=parameters,
                baselines=baselines,
            )

            return ProcessCorrelatedModel(
                random_generator=random_generator,
                config=ProcessCorrelatedConfig(
                    driver_signal=driver_signal,
                    driver_baseline=baselines[
                        driver_signal
                    ],
                    **parameters,
                ),
            )

        if model_name == "slow_thermal":
            driver_signal = parameters.get(
                "driver_signal"
            )

            if driver_signal is not None:
                _validate_driver(
                    logical_name=logical_name,
                    driver_signal=driver_signal,
                    baselines=baselines,
                )

                return SlowThermalModel(
                    random_generator=random_generator,
                    config=SlowThermalConfig(
                        driver_baseline=baselines[
                            driver_signal
                        ],
                        **parameters,
                    ),
                )

            return SlowThermalModel(
                random_generator=random_generator,
                config=SlowThermalConfig(
                    **parameters
                ),
            )

    except TypeError as exc:
        raise ConfigurationError(
            f"Invalid parameters for model '{model_name}' "
            f"of signal '{logical_name}': {exc}"
        ) from exc

    raise ConfigurationError(
        f"Unsupported model '{model_name}' "
        f"for signal '{logical_name}'."
    )


def _resolve_driver(
    *,
    logical_name: str,
    parameters: dict[str, Any],
    baselines: dict[str, float],
) -> str:
    """
    Resolve o driver obrigatório de um modelo correlacionado.
    """

    driver_signal = parameters.pop(
        "driver_signal",
        None,
    )

    if driver_signal is None:
        raise ConfigurationError(
            f"Signal '{logical_name}' requires "
            "'driver_signal'."
        )

    _validate_driver(
        logical_name=logical_name,
        driver_signal=driver_signal,
        baselines=baselines,
    )

    return driver_signal


def _validate_driver(
    *,
    logical_name: str,
    driver_signal: str,
    baselines: dict[str, float],
) -> None:
    """
    Valida uma dependência entre sinais.
    """

    if driver_signal not in baselines:
        raise ConfigurationError(
            f"Signal '{logical_name}' references unknown "
            f"driver '{driver_signal}'."
        )

    if driver_signal == logical_name:
        raise ConfigurationError(
            f"Signal '{logical_name}' cannot use itself as driver."
        )


def _build_scenario_engine(
    *,
    scenario_config: dict[str, Any],
    known_signals: set[str],
) -> ScenarioEngine:
    """
    Constrói o ScenarioEngine e valida referências cruzadas.
    """

    model_config = scenario_config[
        "scenario_model"
    ]

    try:
        modifiers = {
            logical_name: float(value)
            for logical_name, value
            in scenario_config["modifiers"].items()
        }
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(
            "All scenario modifiers must be numeric."
        ) from exc

    if any(
        value < 0
        for value in modifiers.values()
    ):
        raise ConfigurationError(
            "Scenario modifiers cannot be negative."
        )

    try:
        default_scenario = model_config[
            "default_scenario"
        ]
    except KeyError as exc:
        raise ConfigurationError(
            "'scenario_model.default_scenario' is required."
        ) from exc

    default_transition = float(
        model_config
        .get("transition", {})
        .get(
            "default_duration_seconds",
            0.0,
        )
    )

    if default_transition < 0:
        raise ConfigurationError(
            "Default transition duration cannot be negative."
        )

    scenarios: dict[
        str,
        ScenarioDefinition,
    ] = {}

    for logical_name, config in (
        scenario_config["scenarios"].items()
    ):
        raw_effects = config.get(
            "effects",
            {}
        )

        effects: dict[
            str,
            ScenarioEffect,
        ] = {}

        for signal_name, effect in raw_effects.items():
            if signal_name not in known_signals:
                raise ConfigurationError(
                    f"Scenario '{logical_name}' references "
                    f"unknown signal '{signal_name}'."
                )

            effects[signal_name] = ScenarioEffect(
                level=effect.get(
                    "level"
                ),
                target=effect.get(
                    "target"
                ),
            )

        transition_seconds = float(
            config.get(
                "transition_seconds",
                default_transition,
            )
        )

        if transition_seconds < 0:
            raise ConfigurationError(
                f"Scenario '{logical_name}' has a negative "
                "transition duration."
            )

        scenarios[logical_name] = ScenarioDefinition(
            logical_name=logical_name,
            transition_seconds=transition_seconds,
            effects=effects,
        )

    if default_scenario not in scenarios:
        raise ConfigurationError(
            f"Default scenario '{default_scenario}' "
            "is not defined."
        )

    default_modifier = modifiers.get(
        "nominal",
        1.0,
    )

    return ScenarioEngine(
        scenarios=scenarios,
        modifiers=modifiers,
        default_scenario = process_config["simulation"]["default_scenario"]
        default_modifier=default_modifier,
    )
