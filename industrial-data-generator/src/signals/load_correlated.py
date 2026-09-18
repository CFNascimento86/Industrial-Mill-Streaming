from __future__ import annotations
from dataclasses import dataclass
from random import Random
from .base import SignalContext, SignalModel


@dataclass(frozen=True)
class LoadCorrelatedConfig:
    """
    Configuração de um sinal correlacionado à carga do processo.

    driver_signal:
        Variável utilizada como referência de carga.

    driver_baseline:
        Valor nominal da variável de referência.

    sensitivity:
        Intensidade com que o sinal responde às variações da carga.

        Exemplo:
            sensitivity = 1.0
                acompanha proporcionalmente a carga.

            sensitivity = 0.5
                responde com metade da variação relativa da carga.

            sensitivity = 1.5
                responde de forma amplificada.

    variation_fraction:
        Pequena variação natural aplicada ao valor-alvo.

    response_rate:
        Velocidade de convergência para o alvo.

    min_factor / max_factor:
        Limites relativos ao baseline do próprio sinal.
    """

    driver_signal: str
    driver_baseline: float

    sensitivity: float = 1.0
    variation_fraction: float = 0.015
    response_rate: float = 0.35
    min_factor: float = 0.20
    max_factor: float = 1.60


class LoadCorrelatedModel(SignalModel):
    """
    Modelo utilizado para grandezas que respondem à carga do processo.
    A carga relativa é obtida comparando o valor atual da variável motriz
    com seu baseline:

        relative_load = driver_value / driver_baseline

    O sinal correlacionado responde proporcionalmente a essa variação,
    ajustada por sua sensibilidade e pelo modificador do cenário.
    """

    def __init__(
        self,
        *,
        random_generator: Random,
        config: LoadCorrelatedConfig,
    ) -> None:
        super().__init__(random_generator)

        if config.driver_baseline <= 0:
            raise ValueError(
                "driver_baseline must be greater than zero."
            )

        if config.sensitivity < 0:
            raise ValueError(
                "sensitivity cannot be negative."
            )

        
        if config.variation_fraction < 0:
            raise ValueError(
                "variation_fraction cannot be negative."
            )

        if config.response_rate <= 0:
            raise ValueError(
                "response_rate must be greater than zero."
            )

        if config.min_factor < 0:
            raise ValueError(
                "min_factor cannot be negative."
            )

        if config.max_factor < config.min_factor:
            raise ValueError(
                "max_factor cannot be lower than min_factor."
            )

        self._config = config
        
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
        Calcula o próximo valor do sinal correlacionado à carga.
        """

        if dt <= 0:
            raise ValueError("dt must be greater than zero.")

        if baseline <= 0:
            raise ValueError("baseline must be greater than zero.")

        if modifier < 0:
            raise ValueError("modifier cannot be negative.")

        driver_value = context.get(
            self._config.driver_signal
        )

        relative_load = (
            driver_value / self._config.driver_baseline
        )

        load_deviation = relative_load - 1.0

        correlated_factor = (
            1.0
            + load_deviation * self._config.sensitivity
        )

        target = (
            baseline
            * correlated_factor
            * modifier
        )

        variation = self._random.uniform(
            -self._config.variation_fraction,
            self._config.variation_fraction,
        )

        noisy_target = target + (
            baseline * variation
        )

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
