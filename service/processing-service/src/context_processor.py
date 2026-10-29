from __future__ import annotations
from typing import Protocol

from processing_service.context import (
    ContextTransition,
)

from processing_service.contract import (
    TelemetryObservation,
)

from processing_service.load_condition import (
    MillingFeedLoadInferer,
)


class ContextPublisher(
    Protocol
):
    def publish(
        self,
        transition: ContextTransition,
    ) -> None:
        ...


class OperationalContextProcessor:
    """
    Coordena inferência e publicação.

    Ordem obrigatória:

        infer
          ↓
        publish
          ↓
        accept

    Se publish falhar, accept não ocorre.
    """

    def __init__(
        self,
        *,
        inferer: MillingFeedLoadInferer,
        publisher: ContextPublisher,
    ) -> None:
        self._inferer = inferer
        self._publisher = publisher

    def process(
        self,
        observation: TelemetryObservation,
    ) -> ContextTransition | None:

        transition = (
            self._inferer.infer(
                observation
            )
        )

        if transition is None:
            return None

        # Este ponto pode bloquear enquanto
        # Kafka estiver indisponível.
        self._publisher.publish(
            transition
        )

        # Somente delivery confirmado permite
        # modificar o estado do inferer.
        self._inferer.accept(
            transition
        )

        return transition
