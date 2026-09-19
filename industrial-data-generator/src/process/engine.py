from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping
from .state import ProcessState
from scenarios.engine import ScenarioEngine
from signals.base import SignalContext, SignalModel


@dataclass(frozen=True)
class SignalDefinition:
    """
    Define os elementos necessários para executar um sinal no ProcessEngine.

    baseline:
        Valor nominal sintético da variável.

    model:
        Implementação responsável por calcular a evolução temporal do sinal.
    """

    baseline: float
    model: SignalModel


class ProcessEngine:
    """
    Coordena a evolução temporal do processo industrial sintético.

    Em cada ciclo:

        1. avança o ScenarioEngine;
        2. captura um snapshot imutável do estado atual;
        3. calcula todos os próximos valores a partir desse mesmo snapshot;
        4. aplica as atualizações em conjunto;
        5. retorna o novo snapshot do processo.

    O ProcessEngine não conhece S7, OPC UA, Kafka ou persistência.
    """

    def __init__(
        self,
        *,
        state: ProcessState,
        scenario_engine: ScenarioEngine,
        signals: Mapping[str, SignalDefinition],
    ) -> None:
        if not signals:
            raise ValueError(
                "At least one signal definition is required."
            )

        self._state = state
        self._scenario_engine = scenario_engine
        self._signals = dict(signals)
        self._validate_configuration()

    @property
    def state(self) -> ProcessState:
        """
        Retorna o estado atual do processo.
        """
        return self._state

    @property
    def scenario_engine(self) -> ScenarioEngine:
        """
        Retorna o ScenarioEngine utilizado pelo processo.
        """
        return self._scenario_engine

    def step(self, dt: float) -> dict[str, float]:
        """
        Executa um ciclo de evolução do processo.
        Todos os modelos calculam seus próximos valores usando o mesmo
        snapshot de estado, impedindo dependências acidentais da ordem
        de execução.

        Args:
            dt:
                Intervalo temporal do ciclo, em segundos.

        Returns:
            Snapshot atualizado do processo.
        """

        if dt <= 0:
            raise ValueError("dt must be greater than zero.")

        self._scenario_engine.step(dt)

        current_snapshot = self._state.snapshot()

        context = SignalContext(
            values=current_snapshot
        )

        next_values: dict[str, float] = {}

        for logical_name, definition in self._signals.items():
            current_value = current_snapshot[logical_name]

            modifier = self._scenario_engine.get_modifier(
                logical_name
            )

           next_values[logical_name] = (
                definition.model.next_value(
                    current_value=current_value,
                    baseline=definition.baseline,
                    modifier=modifier,
                    context=context,
                    dt=dt,
                )
            )

        timestamp = datetime.now(
            timezone.utc
        )
        
       self._commit(
            next_values,
            timestamp=timestamp,
        )

        return self._state.snapshot()

    def set_scenario(
        self,
        logical_name: str,
        *,
        transition_seconds: float | None = None,
    ) -> None:
        """
        Solicita uma mudança de cenário operacional.
        O ProcessEngine apenas encaminha a solicitação ao ScenarioEngine.
        """

        self._scenario_engine.set_scenario(
            logical_name,
            transition_seconds=transition_seconds,
        )

    def snapshot(self) -> dict[str, float]:
        """
        Retorna o snapshot atual sem avançar a simulação.
        """
        return self._state.snapshot()

    def _commit(
        self,
        next_values: Mapping[str, float],
        *,
        timestamp: datetime,
    ) -> None:
        """
        Aplica em conjunto os valores calculados para o novo ciclo.
        """

        for logical_name, value in next_values.items():
            self._state.update_signal(
                logical_name=logical_name,
                value=value,
                timestamp=timestamp,
            )

    def _validate_configuration(self) -> None:
        """
        Valida a consistência entre ProcessState e definições de sinais.
        """

        state_signals = set(self._state.signals)
        configured_signals = set(self._signals)

        missing_in_state = (
            configured_signals - state_signals
        )

        if missing_in_state:
            missing = ", ".join(
                sorted(missing_in_state)
            )

            raise ValueError(
                "Signals configured in ProcessEngine are not registered "
                f"in ProcessState: {missing}"
            )

        missing_definition = (
            state_signals - configured_signals
        )

        if missing_definition:
            missing = ", ".join(
                sorted(missing_definition)
            )

            raise ValueError(
                "Signals registered in ProcessState do not have a "
                f"SignalDefinition: {missing}"
            )

        for logical_name, definition in self._signals.items():
            if definition.baseline <= 0:
                raise ValueError(
                    f"Baseline for signal '{logical_name}' "
                    "must be greater than zero."
                )
