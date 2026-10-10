from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import (
    HTTPError,
    URLError,
)
from urllib.parse import quote
from urllib.request import (
    Request,
    urlopen,
)


class RegistryError(RuntimeError):
    """
    Falha ao resolver contrato no Schema Registry.
    """


class RegistryContractError(RegistryError):
    """
    O Registry respondeu, mas o contrato encontrado
    não corresponde ao que o IMS espera.
    """


@dataclass(frozen=True)
class RegisteredAvroSchema:
    """
    Representa uma versão de schema Avro
    resolvida no Apicurio Registry.
    """

    group_id: str
    artifact_id: str
    version: str

    global_id: int
    content_id: int

    artifact_type: str
    state: str

    schema: dict[str, Any]


class ApicurioRegistryClient:
    """
    Cliente read-only para resolução de contratos
    no Apicurio Registry Core API v3.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
    ) -> None:
        if not base_url.strip():
            raise ValueError(
                "Registry base URL cannot be empty."
            )

        if timeout <= 0:
            raise ValueError(
                "Registry timeout must be greater than zero."
            )

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def resolve_avro_schema(
        self,
        *,
        group_id: str,
        artifact_id: str,
        version: str,
    ) -> RegisteredAvroSchema:
        """
        Resolve metadata e conteúdo de uma versão
        Avro específica.
        Nenhuma operação de escrita é executada.
        """

        group = quote(
            group_id,
            safe="",
        )

        artifact = quote(
            artifact_id,
            safe="",
        )

        version_expression = quote(
            version,
            safe="",
        )

        artifact_path = (
            f"/groups/{group}"
            f"/artifacts/{artifact}"
        )

        version_path = (
            f"{artifact_path}"
            f"/versions/{version_expression}"
        )

        artifact_metadata = self._get_json(
            artifact_path
        )

        artifact_type = _require_string(
            artifact_metadata,
            "artifactType",
            context="artifact metadata",
        )

        if artifact_type != "AVRO":
            raise RegistryContractError(
                f"Artifact '{group_id}/"
                f"{artifact_id}' has type "
                f"'{artifact_type}', expected 'AVRO'."
            )

        version_metadata = self._get_json(
            version_path
        )

        resolved_group_id = _require_string(
            version_metadata,
            "groupId",
            context="version metadata",
        )

        resolved_artifact_id = _require_string(
            version_metadata,
            "artifactId",
            context="version metadata",
        )

        resolved_version = _require_string(
            version_metadata,
            "version",
            context="version metadata",
        )

        global_id = _require_integer(
            version_metadata,
            "globalId",
            context="version metadata",
        )

        content_id = _require_integer(
            version_metadata,
            "contentId",
            context="version metadata",
        )

        state = _require_string(
            version_metadata,
            "state",
            context="version metadata",
        )

        if resolved_group_id != group_id:
            raise RegistryContractError(
                "Resolved group ID differs from "
                f"requested group ID: "
                f"'{resolved_group_id}'."
            )

        if resolved_artifact_id != artifact_id:
            raise RegistryContractError(
                "Resolved artifact ID differs from "
                f"requested artifact ID: "
                f"'{resolved_artifact_id}'."
            )

        if resolved_version != version:
            raise RegistryContractError(
                "Resolved version differs from "
                f"requested version: "
                f"'{resolved_version}'."
            )

        if state == "DISABLED":
            raise RegistryContractError(
                f"Schema version '{version}' is disabled."
            )

        if state not in {
            "ENABLED",
            "DEPRECATED",
        }:
            raise RegistryContractError(
                f"Unsupported schema state '{state}'."
            )

        schema = self._get_json(
            f"{version_path}/content"
        )

        return RegisteredAvroSchema(
            group_id=resolved_group_id,
            artifact_id=resolved_artifact_id,
            version=resolved_version,
            global_id=global_id,
            content_id=content_id,
            artifact_type=artifact_type,
            state=state,
            schema=schema,
        )

    def _get_json(
        self,
        path: str,
    ) -> dict[str, Any]:
        url = (
            f"{self._base_url}/"
            f"{path.lstrip('/')}"
        )

        request = Request(
            url=url,
            method="GET",
            headers={
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                raw_body = response.read()

        except HTTPError as exc:
            body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

            raise RegistryError(
                f"Apicurio request failed: "
                f"GET {url} -> HTTP {exc.code}. "
                f"Response: {body}"
            ) from exc

        except URLError as exc:
            raise RegistryError(
                f"Could not reach Apicurio Registry "
                f"at '{url}': {exc.reason}"
            ) from exc

        try:
            decoded = raw_body.decode(
                "utf-8"
            )

            result = json.loads(
                decoded
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise RegistryContractError(
                f"Apicurio returned invalid JSON "
                f"for GET {url}."
            ) from exc

        if not isinstance(
            result,
            dict,
        ):
            raise RegistryContractError(
                f"Expected JSON object from "
                f"GET {url}."
            )

        return result


def _require_string(
    payload: dict[str, Any],
    field: str,
    *,
    context: str,
) -> str:
    value = payload.get(
        field
    )

    if not isinstance(
        value,
        str,
    ) or not value:
        raise RegistryContractError(
            f"Field '{field}' is missing or invalid "
            f"in {context}."
        )

    return value


def _require_integer(
    payload: dict[str, Any],
    field: str,
    *,
    context: str,
) -> int:
    value = payload.get(
        field
    )

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise RegistryContractError(
            f"Field '{field}' is missing or invalid "
            f"in {context}."
        )

    return value
