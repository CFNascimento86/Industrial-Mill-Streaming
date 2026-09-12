from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict


@dataclass
class SignalState:
    """
    Representa o estado atual de uma variável industrial sintética.
    O SignalState mantém somente informações necessárias para a evolução
    temporal do sinal. Regras de comportamento permanecem nos SignalModels.
    """

    logical_name: str
    current_value: float
    previous_value: float | None = None
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update(self, value: float, timestamp: datetime | None = None) -> None:
        """
        Atualiza o valor atual preservando o valor anterior.
        """

        self.previous_value = self.current_value
        self.current_value = value
        self.updated_at = timestamp or datetime.now(timezone.utc)


@dataclass
class ProcessState:
    """
    Representa o estado completo do processo industrial sintético.
    O estado é mantido em memória e evolui a cada ciclo do ProcessEngine.
    """

    signals: Dict[str, SignalState] = field(default_factory=dict)

    def register_signal(
        self,
        logical_name: str,
        initial_value: float,
    ) -> SignalState:
        """
        Registra uma variável no estado do processo.
        Uma variável não pode ser registrada mais de uma vez.
        """

        if logical_name in self.signals:
            raise ValueError(
                f"Signal '{logical_name}' is already registered."
            )

        signal = SignalState(
            logical_name=logical_name,
            current_value=initial_value,
        )

        self.signals[logical_name] = signal

        return signal

    def get_signal(self, logical_name: str) -> SignalState:
        """
        Retorna o estado de uma variável registrada.
        """

        try:
            return self.signals[logical_name]
        except KeyError as exc:
            raise KeyError(
                f"Signal '{logical_name}' is not registered."
            ) from exc

    def get_value(self, logical_name: str) -> float:
        """
        Retorna somente o valor atual de uma variável.
        """

        return self.get_signal(logical_name).current_value

    def update_signal(
        self,
        logical_name: str,
        value: float,
        timestamp: datetime | None = None,
    ) -> None:
        """
        Atualiza uma variável existente.
        """

        signal = self.get_signal(logical_name)
        signal.update(value=value, timestamp=timestamp)

    def snapshot(self) -> Dict[str, float]:
        """
        Retorna uma fotografia simples dos valores atuais do processo.
        O snapshot não expõe detalhes internos de estado e pode ser utilizado
        pelas camadas posteriores do gerador.
        """

        return {
            logical_name: signal.current_value
            for logical_name, signal in self.signals.items()
        }
