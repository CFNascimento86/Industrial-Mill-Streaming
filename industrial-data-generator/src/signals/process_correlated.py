from __future__ import annotations
from dataclasses import dataclass
from .base import SignalContext, SignalModel


@dataclass(frozen=True)
class ProcessCorrelatedConfig:
    """
    Configuração de um sinal correlacionado a outra variável de processo.

    driver_signal:
        Variável utilizada como referência para a correlação.

    driver_baseline:
        Valor nominal da variável de referência.

    sensitivity:
        Intensidade da resposta relativa ao desvio do driver em relação
        ao seu baseline.

        Exemplo:
            sensitivity = 1.0
                acompanha proporcionalmente o desvio do driver.

            sensitivity = 0.7
                responde de forma mais amortecida.

            sensitivity = 1.2
                responde de forma mais intensa.

    variation_fraction:
        Pequena variação natural aplicada ao alvo.

    response_rate:
        Velocidade de convergência para o alvo.

    min_factor / max_factor:
        Limites relativos ao baseline do próprio sinal.
    """

    driver_signal: str
    driver_baseline: float

    sensitivity: float = 1.0
    variation_fraction: float = 0.015
    response_rate: float = 0.30

    min_factor: float = 0.20
    max_factor: float = 1.60


class ProcessCorrelatedModel(SignalModel):
    """
    Modelo para sinais cuja evolução está correlacionada a outra grandeza
    do processo industrial.

    A relação é baseada no desvio relativo da variável de referência:

        relative_driver = driver_value / driver_baseline

    O sinal responde a esse desvio de acordo com sua sensibilidade e com
    eventuais modificadores adicionais fornecidos pelo cenário.
    """

    def __init__(
        self,
        *,
        random_generator,
        config: ProcessCorrelatedConfig,
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
        Calcula o próximo valor do sinal correlacionado ao processo.
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

        relative_driver = (
            driver_value / self._config.driver_baseline
        )

        driver_deviation = relative_driver - 1.0

        correlated_factor = (
            1.0
            + driver_deviation * self._config.sensitivity
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
