from __future__ import annotations
from dataclasses import dataclass
from random import Random
from .base import SignalContext, SignalModel


@dataclass(frozen=True)
class ProcessDriverConfig:
    """
    Configuração de um sinal que atua como variável motriz do processo.

    variation_fraction:
        Amplitude máxima da variação natural em torno do valor-alvo,
        expressa como fração do baseline.

    response_rate:
        Velocidade com que o sinal converge para o alvo determinado
        pelo cenário.

    min_factor / max_factor:
        Limites relativos ao baseline para manter o sinal dentro da faixa
        definida pelo modelo sintético de referência.
    """

    variation_fraction: float = 0.015
    response_rate: float = 0.35
    min_factor: float = 0.20
    max_factor: float = 1.60


class ProcessDriverModel(SignalModel):
    """
    Modelo utilizado para variáveis que conduzem a dinâmica do processo.
    O alvo é definido principalmente pelo baseline e pelo modificador
    operacional fornecido pelo ScenarioEngine.
    Outros sinais podem posteriormente utilizar o valor produzido por este
    modelo como referência para correlações de processo.
    """

    def __init__(
        self,
        *,
        random_generator: Random,
        config: ProcessDriverConfig | None = None,
    ) -> None:
        super().__init__(random_generator)

        self._config = config or ProcessDriverConfig()

        if self._config.variation_fraction < 0:
            raise ValueError(
                "variation_fraction cannot be negative."
            )

        if self._config.response_rate <= 0:
            raise ValueError(
                "response_rate must be greater than zero."
            )

        if self._config.min_factor < 0:
            raise ValueError(
                "min_factor cannot be negative."
            )

        if self._config.max_factor < self._config.min_factor:
            raise ValueError(
                "max_factor cannot be lower than min_factor."
            )

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
        Calcula o próximo valor da variável motriz.
        O contexto não é utilizado diretamente porque este modelo representa
        uma variável primária do processo, e não uma resposta a outro sinal.
        """

        if dt <= 0:
            raise ValueError("dt must be greater than zero.")

        if baseline <= 0:
            raise ValueError("baseline must be greater than zero.")

        if modifier < 0:
            raise ValueError("modifier cannot be negative.")

        target = baseline * modifier

        variation = self._random.uniform(
            -self._config.variation_fraction,
            self._config.variation_fraction,
        )

        noisy_target = target + (baseline * variation)

        response = min(
            self._config.response_rate * dt,
            1.0,
        )

        next_value = current_value + (
            noisy_target - current_value
        ) * response

        minimum = baseline * self._config.min_factor
        maximum = baseline * self._config.max_factor

        return max(
            minimum,
            min(next_value, maximum),
        )
