from __future__ import annotations
from dataclasses import dataclass
from .base import SignalContext, SignalModel


@dataclass(frozen=True)
class BoundedVariationConfig:
    """
    Configuração do modelo de variação limitada.

    variation_fraction:
        Amplitude máxima de variação aleatória em torno do alvo,
        expressa como fração do baseline.

        Exemplo:
            0.02 -> ±2% do baseline.

    response_rate:
        Velocidade de convergência do valor atual para o valor-alvo.

        Valores maiores tornam a resposta mais rápida.

    min_factor / max_factor:
        Limites relativos ao baseline utilizados para impedir que o sinal
        evolua para valores incompatíveis com o modelo sintético.
    """

    variation_fraction: float = 0.02
    response_rate: float = 0.25
    min_factor: float = 0.80
    max_factor: float = 1.20


class BoundedVariationModel(SignalModel):
    """
    Modelo para sinais contínuos que permanecem próximos de um valor nominal.
    O valor evolui progressivamente em direção ao alvo definido por:

        target = baseline * modifier

    com pequena variação natural e limites relativos ao baseline.
    """

    def __init__(
        self,
        *,
        random_generator,
        config: BoundedVariationConfig | None = None,
    ) -> None:
        super().__init__(random_generator)

        self._config = config or BoundedVariationConfig()

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
        O contexto não é utilizado neste modelo porque bounded_variation
        representa uma grandeza independente de outras variáveis.
        """

        if dt <= 0:
            raise ValueError("dt must be greater than zero.")

        if baseline <= 0:
            raise ValueError("baseline must be greater than zero.")

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
