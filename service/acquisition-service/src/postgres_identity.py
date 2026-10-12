from __future__ import annotations
from uuid import UUID
import psycopg
from psycopg.rows import dict_row
from acquisition_service.identity import (
    IdentityResolutionError,
    ResolvedIdentity,
)


class PostgresIdentityResolver:
    """
    Resolve identidades industriais persistidas
    no PostgreSQL.
    A resolução é carregada uma única vez na
    inicialização do serviço e mantida em memória.
    """

    def __init__(
        self,
        identities: dict[
            str,
            ResolvedIdentity,
        ],
        *,
        source_logical_name: str,
    ) -> None:
        self._identities = identities
        self._source_logical_name = (
            source_logical_name
        )

    @classmethod
    def from_database(
        cls,
        *,
        database_url: str,
        source_logical_name: str,
        connect_timeout: int = 5,
    ) -> PostgresIdentityResolver:

        query = """
            SELECT
                v.variable_id,
                v.logical_name
                    AS variable_logical_name,

                s.source_id,
                s.logical_name
                    AS source_logical_name

            FROM industrial.variable_source vs

            JOIN industrial.variable v
              ON v.variable_id = vs.variable_id

            JOIN industrial.source s
              ON s.source_id = vs.source_id

            WHERE
                s.logical_name = %s
                AND v.status = 'active'
                AND s.status = 'active'

            ORDER BY
                v.logical_name;
        """

        try:
            with psycopg.connect(
                database_url,
                connect_timeout=connect_timeout,
                row_factory=dict_row,
            ) as connection:

                rows = connection.execute(
                    query,
                    (
                        source_logical_name,
                    ),
                ).fetchall()

        except psycopg.Error as exc:
            raise IdentityResolutionError(
                "Could not load industrial "
                "identities from PostgreSQL."
            ) from exc

        if not rows:
            raise IdentityResolutionError(
                "No active industrial identities "
                f"were found for source "
                f"'{source_logical_name}'."
            )

        identities: dict[
            str,
            ResolvedIdentity,
        ] = {}

        for row in rows:
            logical_name = (
                row[
                    "variable_logical_name"
                ]
            )

            if logical_name in identities:
                raise IdentityResolutionError(
                    "Duplicate active identity "
                    f"for variable '{logical_name}'."
                )

            identities[
                logical_name
            ] = ResolvedIdentity(
                variable_id=UUID(
                    str(
                        row["variable_id"]
                    )
                ),
                variable_logical_name=(
                    logical_name
                ),
                source_id=UUID(
                    str(
                        row["source_id"]
                    )
                ),
                source_logical_name=(
                    row[
                        "source_logical_name"
                    ]
                ),
            )

        return cls(
            identities,
            source_logical_name=(
                source_logical_name
            ),
        )

    def resolve(
        self,
        *,
        variable_logical_name: str,
        source_logical_name: str,
    ) -> ResolvedIdentity:

        if (
            source_logical_name
            != self._source_logical_name
        ):
            raise IdentityResolutionError(
                "Requested source differs from "
                "the resolver source: "
                f"'{source_logical_name}'."
            )

        try:
            return self._identities[
                variable_logical_name
            ]

        except KeyError as exc:
            raise IdentityResolutionError(
                "Industrial identity was not "
                "found for variable "
                f"'{variable_logical_name}' "
                f"and source "
                f"'{source_logical_name}'."
            ) from exc
