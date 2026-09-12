from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from random import Random
from typing import Mapping


@dataclass(frozen=True)
class SignalContext:
    """
    Contexto disponibilizado ao modelo de sinal durante um ciclo de simulação.
    Permite que modelos correlacionados consultem outras grandezas do processo
    sem criar dependência direta com ProcessState ou ProcessEngine.
    """

    values: Mapping[str, float] = field(default_factory=dict)

    def get(self, logical_name: str) -> float:
        """
        Retorna o valor atual de uma variável disponível no contexto.
        Uma dependência ausente é tratada como erro de configuração.
        """

        try:
            return self.values[logical_name]
        except KeyError as exc:
            raise KeyError(
                f"Signal '{logical_name}' is not available in the context."
            ) from exc


class SignalModel(ABC):
    """
    Contrato base para modelos de comportamento de sinais industriais.
    Um SignalModel calcula o próximo valor de uma variável a partir de seu
    estado atual, baseline, influência do cenário, contexto do processo e
    intervalo temporal da simulação.
    """

    def __init__(self, random_generator: Random) -> None:
        """
        Recebe um gerador pseudoaleatório externo para preservar
        reprodutibilidade entre execuções.
        """

        self._random = random_generator

    @abstractmethod
    def next_value(
        self,
        *,
        current_value: float,
        baseline: float,
        modifier: float,
        context: SignalContext,
        dt: float,
    ) -> float:
        """
        Calcula o próximo valor do sinal.

        Args:
            current_value:
                Valor atual da variável.

            baseline:
                Valor nominal definido pelo modelo sintético do processo.

            modifier:
                Modificador produzido pelo ScenarioEngine.

                Exemplo:
                    1.00 -> nominal
                    1.25 -> condição elevada
                    0.70 -> condição reduzida

            context:
                Snapshot parcial ou completo das demais variáveis disponíveis
                para correlações entre sinais.

            dt:
                Intervalo de tempo, em segundos, desde o último ciclo.

        Returns:
            Próximo valor da variável.
        """

        raise NotImplementedError
