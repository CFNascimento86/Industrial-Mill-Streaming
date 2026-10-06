from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


class IdentityResolutionError(ValueError):
    pass


@dataclass(frozen=True)
class ResolvedIdentity:
    """
    Identidade industrial resolvida para uma observação.
    """

    variable_id: UUID
    variable_logical_name: str

    source_id: UUID
    source_logical_name: str


class IdentityResolver(Protocol):
    """
    Contrato para resolução de identidade industrial.
    A implementação concreta poderá utilizar posteriormente:
        variables.yaml
        sources.yaml
        variable_sources.yaml
    """

    def resolve(
        self,
        *,
        variable_logical_name: str,
        source_logical_name: str,
    ) -> ResolvedIdentity:
        ...
