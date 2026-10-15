from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_DNS, UUID, uuid5
import psycopg
import yaml


class BootstrapError(RuntimeError):
    """Falha durante o bootstrap do modelo industrial."""


DATABASE_DIR = Path(__file__).resolve().parent

IMS_IDENTITY_NAMESPACE = uuid5(
    NAMESPACE_DNS,
    "industrial-mill-streaming.ims",
)


def deterministic_id(
    entity_type: str,
    logical_name: str,
) -> UUID:
    """
    Gera identidade determinística apenas para entidades novas.
    Se a entidade já existir no PostgreSQL, o UUID persistido
    será preservado pelo UPSERT.
    """
    return uuid5(
        IMS_IDENTITY_NAMESPACE,
        f"{entity_type}:{logical_name}",
    )


def load_seed(
    filename: str,
    root_key: str,
) -> list[dict[str, Any]]:
    path = DATABASE_DIR / filename

    if not path.exists():
        raise BootstrapError(
            f"Seed file not found: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            document = yaml.safe_load(file)

    except yaml.YAMLError as exc:
        raise BootstrapError(
            f"Invalid YAML in '{filename}': {exc}"
        ) from exc

    if not isinstance(document, dict):
        raise BootstrapError(
            f"Seed '{filename}' must contain a YAML object."
        )

    records = document.get(root_key)

    if not isinstance(records, list):
        raise BootstrapError(
            f"Seed '{filename}' must contain "
            f"a '{root_key}' list."
        )

    return records


def index_by_logical_name(
    records: list[dict[str, Any]],
    *,
    entity_name: str,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for record in records:
        logical_name = record.get(
            "logical_name"
        )

        if not isinstance(logical_name, str):
            raise BootstrapError(
                f"{entity_name} without valid logical_name."
            )

        if logical_name in result:
            raise BootstrapError(
                f"Duplicate {entity_name} logical_name: "
                f"'{logical_name}'."
            )

        result[logical_name] = record

    return result


def validate_seeds(
    *,
    processes: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
    variables: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    variable_sources: list[dict[str, Any]],
) -> None:
    """
    Valida referências antes de modificar o PostgreSQL.
    """

    for asset in assets.values():
        process_name = asset.get("process")

        if process_name not in processes:
            raise BootstrapError(
                f"Asset '{asset['logical_name']}' references "
                f"unknown process '{process_name}'."
            )

        parent = asset.get("parent_asset")

        if (
            parent is not None
            and parent not in assets
        ):
            raise BootstrapError(
                f"Asset '{asset['logical_name']}' references "
                f"unknown parent_asset '{parent}'."
            )

    for variable in variables.values():
        asset_name = variable.get("asset")

        if asset_name not in assets:
            raise BootstrapError(
                f"Variable '{variable['logical_name']}' "
                f"references unknown asset '{asset_name}'."
            )

    seen_relations: set[
        tuple[str, str]
    ] = set()

    for relation in variable_sources:
        variable_name = relation.get("variable")
        source_name = relation.get("source")

        if variable_name not in variables:
            raise BootstrapError(
                f"Variable-source relation references "
                f"unknown variable '{variable_name}'."
            )

        if source_name not in sources:
            raise BootstrapError(
                f"Variable-source relation references "
                f"unknown source '{source_name}'."
            )

        key = (
            variable_name,
            source_name,
        )

        if key in seen_relations:
            raise BootstrapError(
                "Duplicate variable-source relation: "
                f"{variable_name} -> {source_name}."
            )

        seen_relations.add(key)


def upsert_processes(
    connection: psycopg.Connection,
    processes: dict[str, dict[str, Any]],
) -> dict[str, UUID]:
    ids: dict[str, UUID] = {}

    query = """
        INSERT INTO industrial.process (
            process_id,
            logical_name,
            display_name,
            description,
            status
        )
        VALUES (%s, %s, %s, %s, %s)

        ON CONFLICT (logical_name)
        DO UPDATE SET
            display_name = EXCLUDED.display_name,
            description = EXCLUDED.description,
            status = EXCLUDED.status

        RETURNING process_id;
    """

    for logical_name, record in processes.items():
        process_id = connection.execute(
            query,
            (
                deterministic_id(
                    "process",
                    logical_name,
                ),
                logical_name,
                record["display_name"],
                record.get("description"),
                record["status"],
            ),
        ).fetchone()[0]

        ids[logical_name] = process_id

    return ids


def upsert_assets(
    connection: psycopg.Connection,
    assets: dict[str, dict[str, Any]],
    process_ids: dict[str, UUID],
) -> dict[str, UUID]:
    """
    Persiste ativos respeitando a hierarquia de parent_asset.
    """

    ids: dict[str, UUID] = {}
    pending = dict(assets)

    query = """
        INSERT INTO industrial.asset (
            asset_id,
            logical_name,
            display_name,
            process_id,
            parent_asset_id,
            asset_type,
            description,
            status
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )

        ON CONFLICT (logical_name)
        DO UPDATE SET
            display_name = EXCLUDED.display_name,
            process_id = EXCLUDED.process_id,
            parent_asset_id = EXCLUDED.parent_asset_id,
            asset_type = EXCLUDED.asset_type,
            description = EXCLUDED.description,
            status = EXCLUDED.status

        RETURNING asset_id;
    """

    while pending:
        progress = False

        for logical_name, record in list(
            pending.items()
        ):
            parent_name = record.get(
                "parent_asset"
            )

            if (
                parent_name is not None
                and parent_name not in ids
            ):
                continue

            parent_id = (
                ids[parent_name]
                if parent_name is not None
                else None
            )

            asset_id = connection.execute(
                query,
                (
                    deterministic_id(
                        "asset",
                        logical_name,
                    ),
                    logical_name,
                    record["display_name"],
                    process_ids[
                        record["process"]
                    ],
                    parent_id,
                    record["asset_type"],
                    record.get("description"),
                    record["status"],
                ),
            ).fetchone()[0]

            ids[logical_name] = asset_id

            del pending[logical_name]
            progress = True

        if not progress:
            unresolved = ", ".join(
                sorted(pending)
            )

            raise BootstrapError(
                "Could not resolve asset hierarchy. "
                f"Pending assets: {unresolved}"
            )

    return ids


def upsert_variables(
    connection: psycopg.Connection,
    variables: dict[str, dict[str, Any]],
    asset_ids: dict[str, UUID],
) -> dict[str, UUID]:
    ids: dict[str, UUID] = {}

    query = """
        INSERT INTO industrial.variable (
            variable_id,
            logical_name,
            catalog_item_logical_name,
            asset_id,
            status
        )
        VALUES (%s, %s, %s, %s, %s)

        ON CONFLICT (logical_name)
        DO UPDATE SET
            catalog_item_logical_name =
                EXCLUDED.catalog_item_logical_name,
            asset_id = EXCLUDED.asset_id,
            status = EXCLUDED.status

        RETURNING variable_id;
    """

    for logical_name, record in variables.items():
        variable_id = connection.execute(
            query,
            (
                deterministic_id(
                    "variable",
                    logical_name,
                ),
                logical_name,
                record["catalog_item"],
                asset_ids[
                    record["asset"]
                ],
                record["status"],
            ),
        ).fetchone()[0]

        ids[logical_name] = variable_id

    return ids


def upsert_sources(
    connection: psycopg.Connection,
    sources: dict[str, dict[str, Any]],
) -> dict[str, UUID]:
    ids: dict[str, UUID] = {}

    query = """
        INSERT INTO industrial.source (
            source_id,
            logical_name,
            display_name,
            source_type,
            description,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s)

        ON CONFLICT (logical_name)
        DO UPDATE SET
            display_name = EXCLUDED.display_name,
            source_type = EXCLUDED.source_type,
            description = EXCLUDED.description,
            status = EXCLUDED.status

        RETURNING source_id;
    """

    for logical_name, record in sources.items():
        source_id = connection.execute(
            query,
            (
                deterministic_id(
                    "source",
                    logical_name,
                ),
                logical_name,
                record["display_name"],
                record["source_type"],
                record.get("description"),
                record["status"],
            ),
        ).fetchone()[0]

        ids[logical_name] = source_id

    return ids


def upsert_variable_sources(
    connection: psycopg.Connection,
    relations: list[dict[str, Any]],
    variable_ids: dict[str, UUID],
    source_ids: dict[str, UUID],
) -> int:
    query = """
        INSERT INTO industrial.variable_source (
            variable_id,
            source_id
        )
        VALUES (%s, %s)

        ON CONFLICT (
            variable_id,
            source_id
        )
        DO NOTHING;
    """

    for relation in relations:
        connection.execute(
            query,
            (
                variable_ids[
                    relation["variable"]
                ],
                source_ids[
                    relation["source"]
                ],
            ),
        )

    return len(relations)


def bootstrap() -> None:
    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:
        raise BootstrapError(
            "DATABASE_URL is not configured."
        )

    processes_raw = load_seed(
        "processes.yaml",
        "processes",
    )

    assets_raw = load_seed(
        "assets.yaml",
        "assets",
    )

    variables_raw = load_seed(
        "variables.yaml",
        "variables",
    )

    sources_raw = load_seed(
        "sources.yaml",
        "sources",
    )

    variable_sources = load_seed(
        "variables_sources.yaml",
        "variable_sources",
    )

    processes = index_by_logical_name(
        processes_raw,
        entity_name="process",
    )

    assets = index_by_logical_name(
        assets_raw,
        entity_name="asset",
    )

    variables = index_by_logical_name(
        variables_raw,
        entity_name="variable",
    )

    sources = index_by_logical_name(
        sources_raw,
        entity_name="source",
    )

    validate_seeds(
        processes=processes,
        assets=assets,
        variables=variables,
        sources=sources,
        variable_sources=variable_sources,
    )

    try:
        with psycopg.connect(
            database_url
        ) as connection:
            process_ids = upsert_processes(
                connection,
                processes,
            )

            asset_ids = upsert_assets(
                connection,
                assets,
                process_ids,
            )

            variable_ids = upsert_variables(
                connection,
                variables,
                asset_ids,
            )

            source_ids = upsert_sources(
                connection,
                sources,
            )

            relation_count = (
                upsert_variable_sources(
                    connection,
                    variable_sources,
                    variable_ids,
                    source_ids,
                )
            )

    except psycopg.Error as exc:
        raise BootstrapError(
            "PostgreSQL bootstrap failed."
        ) from exc

    print(
        "[SUCCESS] Industrial identity bootstrap completed."
    )

    print(
        f"Processes: {len(process_ids)}"
    )

    print(
        f"Assets: {len(asset_ids)}"
    )

    print(
        f"Variables: {len(variable_ids)}"
    )

    print(
        f"Sources: {len(source_ids)}"
    )

    print(
        f"Variable-source relations: "
        f"{relation_count}"
    )


def main() -> int:
    try:
        bootstrap()
        return 0

    except BootstrapError as exc:
        print(
            f"[ERROR] {exc}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
