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


class RegistryError(
    RuntimeError
):
    """
    Falha de comunicação ou resolução
    no Apicurio Registry.
    """


class RegistryContractError(
    RegistryError
):
    """
    O Registry respondeu, mas o contrato
    encontrado não corresponde ao esperado.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class RegisteredAvroContract:
    """
    Representa uma versão Avro
    governada pelo Apicurio Registry.
    """

    group_id: str
    artifact_id: str
    version: str

    global_id: int
    content_id: int

    state: str

    schema: dict[
        str,
        Any,
    ]


class ApicurioRegistryClient:
    """
    Cliente read-only do Apicurio Registry.

    Responsabilidades:

    - resolver schema pelo contentId
      recebido no wire format;

    - resolver uma versão explícita
      utilizada por producers.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
    ) -> None:

        if not base_url.strip():
            raise ValueError(
                "Registry base URL "
                "cannot be empty."
            )

        if timeout <= 0:
            raise ValueError(
                "Registry timeout "
                "must be positive."
            )

        self._base_url = (
            base_url.rstrip("/")
        )

        self._timeout = timeout

    def resolve_avro_schema_by_content_id(
        self,
        content_id: int,
    ) -> dict[str, Any]:
        """
        Resolve um schema Avro através
        do contentId presente na mensagem.
        """

        if (
            isinstance(
                content_id,
                bool,
            )
            or not isinstance(
                content_id,
                int,
            )
            or content_id <= 0
        ):
            raise ValueError(
                "content_id must be "
                "a positive integer."
            )

        schema = self._get_json_path(
            (
                "/ids/contentIds/"
                f"{content_id}"
            )
        )

        if schema.get(
            "type"
        ) != "record":
            raise RegistryContractError(
                "Expected an Avro "
                "record schema."
            )

        fullname = (
            f"{schema.get('namespace')}."
            f"{schema.get('name')}"
        )

        if fullname != (
            "ims.telemetry."
            "TelemetryObservation"
        ):
            raise RegistryContractError(
                "Unexpected telemetry "
                f"contract: '{fullname}'."
            )

        return schema

    def resolve_avro_contract(
        self,
        *,
        group_id: str,
        artifact_id: str,
        version: str,
    ) -> RegisteredAvroContract:
        """
        Resolve uma versão contratual
        explícita para utilização por
        um producer.
        """

        if not group_id.strip():
            raise ValueError(
                "group_id cannot be empty."
            )

        if not artifact_id.strip():
            raise ValueError(
                "artifact_id cannot be empty."
            )

        if not version.strip():
            raise ValueError(
                "version cannot be empty."
            )

        group = quote(
            group_id,
            safe="",
        )

        artifact = quote(
            artifact_id,
            safe="",
        )

        version_value = quote(
            version,
            safe="",
        )

        version_path = (
            f"/groups/{group}"
            f"/artifacts/{artifact}"
            f"/versions/{version_value}"
        )

        metadata = (
            self._get_json_path(
                version_path
            )
        )

        resolved_group = (
            metadata.get(
                "groupId"
            )
        )

        resolved_artifact = (
            metadata.get(
                "artifactId"
            )
        )

        resolved_version = (
            metadata.get(
                "version"
            )
        )

        content_id = (
            metadata.get(
                "contentId"
            )
        )

        global_id = (
            metadata.get(
                "globalId"
            )
        )

        state = metadata.get(
            "state"
        )

        if (
            resolved_group
            != group_id
        ):
            raise RegistryContractError(
                "Resolved groupId differs "
                "from requested groupId."
            )

        if (
            resolved_artifact
            != artifact_id
        ):
            raise RegistryContractError(
                "Resolved artifactId differs "
                "from requested artifactId."
            )

        if (
            resolved_version
            != version
        ):
            raise RegistryContractError(
                "Resolved version differs "
                "from requested version."
            )

        if (
            not isinstance(
                content_id,
                int,
            )
            or isinstance(
                content_id,
                bool,
            )
            or content_id <= 0
        ):
            raise RegistryContractError(
                "Invalid contentId returned "
                "by Apicurio."
            )

        if (
            not isinstance(
                global_id,
                int,
            )
            or isinstance(
                global_id,
                bool,
            )
        ):
            raise RegistryContractError(
                "Invalid globalId returned "
                "by Apicurio."
            )

        if state not in {
            "ENABLED",
            "DEPRECATED",
        }:
            raise RegistryContractError(
                "Unsupported artifact "
                f"state '{state}'."
            )

        schema = self._get_json_path(
            f"{version_path}/content"
        )

        if schema.get(
            "type"
        ) != "record":
            raise RegistryContractError(
                "Expected an Avro "
                "record schema."
            )

        return RegisteredAvroContract(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
            global_id=global_id,
            content_id=content_id,
            state=state,
            schema=schema,
        )

    def _get_json_path(
        self,
        path: str,
    ) -> dict[str, Any]:
        """
        Executa GET no Registry e exige
        resposta JSON object.
        """

        url = (
            f"{self._base_url}/"
            f"{path.lstrip('/')}"
        )

        request = Request(
            url=url,
            method="GET",
            headers={
                "Accept": (
                    "application/json"
                ),
            },
        )

        try:
            with urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                body = response.read()

        except HTTPError as exc:
            response_body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

            raise RegistryError(
                "Apicurio request failed: "
                f"GET {url} -> "
                f"HTTP {exc.code}. "
                f"Response: {response_body}"
            ) from exc

        except URLError as exc:
            raise RegistryError(
                "Could not reach "
                "Apicurio Registry at "
                f"'{url}': {exc.reason}"
            ) from exc

        try:
            result = json.loads(
                body.decode(
                    "utf-8"
                )
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise RegistryContractError(
                "Apicurio returned "
                "invalid JSON for "
                f"GET {url}."
            ) from exc

        if not isinstance(
            result,
            dict,
        ):
            raise RegistryContractError(
                "Registry response must "
                "be a JSON object."
            )

        return result
