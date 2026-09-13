from __future__ import annotations
from dataclasses import dataclass
from .base import SignalContext, SignalModel


@dataclass(frozen=True)
class SlowThermalConfig:
    """
    Configuração de um sinal térmico com resposta lenta.

    response_rate:
        Velocidade de convergência para o valor-alvo.

        Deve ser significativamente menor do que em modelos de resposta
        mecânica ou de processo, refletindo a inércia térmica.

    variation_fraction:
        Pequena oscilação natural aplicada ao alvo térmico.

    min_factor / max_factor:
        Limites relativos ao baseline da variável.

    driver_signal:
        Variável opcional utilizada para influenciar o alvo térmico.

        Exemplo:
            main_drive_01_torque
            shredder_motor_current
            cane_flow

        Quando ausente, o sinal responde apenas ao baseline e ao
        modificador fornecido pelo cenário.

    driver_baseline:
        Valor nominal do driver.

        Obrigatório quando driver_signal for configurado.

    sensitivity:
        Intensidade da influência relativa do driver sobre o alvo térmico.
    """

    response_rate: float = 0.03
    variation_fraction: float = 0.003

    min_factor: float = 0.80
    max_factor: float = 1.30

    driver_signal: str | None = None
    driver_baseline: float | None = None
    sensitivity: float = 0.20


class SlowThermalModel(SignalModel):
    """
    Modelo para grandezas térmicas com elevada inércia temporal.
    O sinal converge lentamente para um alvo calculado a partir de:

        baseline
        × influência do driver
        × modificador do cenário

    O objetivo não é reproduzir um modelo termodinâmico rigoroso, mas
    representar de forma plausível a resposta lenta de temperaturas
    industriais.
    """

    def __init__(
        self,
        *,
        random_generator,
        config: SlowThermalConfig | None = None,
    ) -> None:
        super().__init__(random_generator)

        self._config = config or SlowThermalConfig()

        if self._config.response_rate <= 0:
            raise ValueError(
                "response_rate must be greater than zero."
            )

        if self._config.variation_fraction < 0:
            raise ValueError(
                "variation_fraction cannot be negative."
            )

        if self._config.sensitivity < 0:
            raise ValueError(
                "sensitivity cannot be negative."
            )

        if self._config.driver_signal is not None:
            if (
                self._config.driver_baseline is None
                or self._config.driver_baseline <= 0
            ):
                raise ValueError(
                    "driver_baseline must be greater than zero "
                    "when driver_signal is configured."
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
        Calcula o próximo valor térmico.
        A resposta é deliberadamente lenta para representar a inércia
        característica de sistemas térmicos industriais.
        """

        if dt <= 0:
            raise ValueError("dt must be greater than zero.")

        if baseline <= 0:
            raise ValueError("baseline must be greater than zero.")

        if modifier < 0:
            raise ValueError("modifier cannot be negative.")

        driver_factor = 1.0

        if self._config.driver_signal is not None:
            driver_value = context.get(
                self._config.driver_signal
            )

            relative_driver = (
                driver_value
                / self._config.driver_baseline
            )

            driver_deviation = relative_driver - 1.0

            driver_factor = (
                1.0
                + driver_deviation
                * self._config.sensitivity
            )

        target = (
            baseline
            * driver_factor
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
