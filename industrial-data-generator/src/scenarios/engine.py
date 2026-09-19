from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class ScenarioEffect:
    """
    Efeito de um cenário sobre uma variável.

    level:
        Nível simbólico resolvido para um modificador numérico.

    target:
        Alvo simbólico utilizado principalmente em cenários de recuperação.

    Apenas um dos dois deve ser informado.
    """

    level: str | None = None
    target: str | None = None

    def __post_init__(self) -> None:
        if self.level is not None and self.target is not None:
            raise ValueError(
                "ScenarioEffect cannot define both 'level' and 'target'."
            )

        if self.level is None and self.target is None:
            raise ValueError(
                "ScenarioEffect must define either 'level' or 'target'."
            )


@dataclass(frozen=True)
class ScenarioDefinition:
    """
    Definição imutável de um cenário operacional sintético.
    """

    logical_name: str
    transition_seconds: float
    effects: Mapping[str, ScenarioEffect] = field(default_factory=dict)


@dataclass
class ScenarioTransition:
    """
    Representa uma transição em andamento entre dois cenários.
    Os modificadores iniciais são capturados no momento da troca de cenário,
    permitindo interpolação contínua até os valores-alvo.
    """

    elapsed_seconds: float
    duration_seconds: float
    initial_modifiers: dict[str, float]
    target_modifiers: dict[str, float]

    @property
    def progress(self) -> float:
        if self.duration_seconds <= 0:
            return 1.0

        return min(
            self.elapsed_seconds / self.duration_seconds,
            1.0,
        )

    @property
    def completed(self) -> bool:
        return self.progress >= 1.0


class ScenarioEngine:
    """
    Gerencia o cenário operacional ativo e resolve seus modificadores.
    O engine não calcula valores industriais. Sua única responsabilidade é
    informar aos SignalModels qual influência relativa deve ser aplicada
    durante o ciclo atual.
    """

    def __init__(
        self,
        *,
        scenarios: Mapping[str, ScenarioDefinition],
        modifiers: Mapping[str, float],
        default_scenario: str,
        default_modifier: float = 1.0,
    ) -> None:
        if default_scenario not in scenarios:
            raise ValueError(
                f"Default scenario '{default_scenario}' is not defined."
            )

        if default_modifier < 0:
            raise ValueError(
                "default_modifier cannot be negative."
            )

        self._scenarios = dict(scenarios)
        self._modifiers = dict(modifiers)
        self._default_modifier = default_modifier

        self._current_scenario = default_scenario
        self._transition: ScenarioTransition | None = None

        self._effective_modifiers = self._resolve_targets(
            self._scenarios[default_scenario]
        )

    @property
    def current_scenario(self) -> str:
        """
        Retorna o cenário atualmente selecionado.
        """
        return self._current_scenario

    @property
    def is_transitioning(self) -> bool:
        """
        Indica se existe uma transição de cenário em andamento.
        """
        return self._transition is not None

    def set_scenario(
        self,
        logical_name: str,
        *,
        transition_seconds: float | None = None,
    ) -> None:
        """
        Inicia a transição para um novo cenário.
        Se transition_seconds não for informado, utiliza o tempo definido
        no próprio ScenarioDefinition.
        """

        if logical_name not in self._scenarios:
            raise KeyError(
                f"Scenario '{logical_name}' is not defined."
            )

        scenario = self._scenarios[logical_name]

        duration = (
            scenario.transition_seconds
            if transition_seconds is None
            else transition_seconds
        )

        if duration < 0:
            raise ValueError(
                "transition_seconds cannot be negative."
            )

        target_modifiers = self._resolve_targets(scenario)

        self._current_scenario = logical_name

        if duration == 0:
            self._effective_modifiers = target_modifiers
            self._transition = None
            return

        all_signals = (
            set(self._effective_modifiers)
            | set(target_modifiers)
        )

        initial = {
            signal: self._effective_modifiers.get(
                signal,
                self._default_modifier,
            )
            for signal in all_signals
        }

        targets = {
            signal: target_modifiers.get(
                signal,
                self._default_modifier,
            )
            for signal in all_signals
        }

         if duration == 0:
            self._effective_modifiers = targets
            self._transition = None
            return

        self._transition = ScenarioTransition(
            elapsed_seconds=0.0,
            duration_seconds=duration,
            initial_modifiers=initial,
            target_modifiers=targets,
        )

    def step(self, dt: float) -> None:
        """
        Avança temporalmente o ScenarioEngine.
        Durante uma transição, os modificadores são interpolados entre o
        estado anterior e o alvo do novo cenário.
        """

        if dt <= 0:
            raise ValueError("dt must be greater than zero.")

        if self._transition is None:
            return

        self._transition.elapsed_seconds += dt

        progress = self._transition.progress

        self._effective_modifiers = {
            signal: self._interpolate(
                start=self._transition.initial_modifiers[signal],
                target=self._transition.target_modifiers[signal],
                progress=progress,
            )
            for signal in self._transition.initial_modifiers
        }

        if self._transition.completed:
            self._effective_modifiers = dict(
                self._transition.target_modifiers
            )
            self._transition = None

    def get_modifier(self, logical_name: str) -> float:
        """
        Retorna o modificador efetivo de uma variável.
        Variáveis não afetadas explicitamente pelo cenário recebem o
        modificador nominal.
        """

        return self._effective_modifiers.get(
            logical_name,
            self._default_modifier,
        )

    def snapshot(self) -> dict[str, float]:
        """
        Retorna uma fotografia dos modificadores efetivos atuais.
        """

        return dict(self._effective_modifiers)

    def _resolve_targets(
        self,
        scenario: ScenarioDefinition,
    ) -> dict[str, float]:
        """
        Converte os níveis simbólicos definidos no YAML em modificadores
        numéricos utilizáveis pelos modelos de sinal.
        """

        targets: dict[str, float] = {}

         for logical_name, effect in scenario.effects.items():
            symbolic_level = (
                effect.level
                if effect.level is not None
                else effect.target

            if symbolic_level not in self._modifiers:
                raise KeyError(
                    f"Modifier '{symbolic_level}' used by signal "
                    f"'{logical_name}' in scenario "
                    f"'{scenario.logical_name}' is not defined."
                )

            targets[logical_name] = self._modifiers[symbolic_level]

        return targets

    @staticmethod
    def _interpolate(
        *,
        start: float,
        target: float,
        progress: float,
    ) -> float:
        """
        Interpolação linear entre dois modificadores.
        """

        return start + (target - start) * progress
