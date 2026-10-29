from __future__ import annotations
import json
from typing import Any
from dataclasses import dataclass
from urllib.parse import quote

from urllib.error import (
    HTTPError,
    URLError,
)

from urllib.request import (
    Request,
    urlopen,
)


class RegistryError(
    RuntimeError
):
    pass


class RegistryContractError(
    RegistryError
):
    pass


class ApicurioRegistryClient:
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
                "Registry timeout must "
                "be positive."
            )

        self._base_url = (
            base_url.rstrip("/")
        )

        self._timeout = timeout

    def resolve_avro_schema_by_content_id(
        self,
        content_id: int,
    ) -> dict[str, Any]:
        if (
            isinstance(content_id, bool)
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

        url = (
            f"{self._base_url}"
            f"/ids/contentIds/"
            f"{content_id}"
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
            raise RegistryError(
                "Apicurio request failed: "
                f"GET {url} -> "
                f"HTTP {exc.code}."
            ) from exc

        except URLError as exc:
            raise RegistryError(
                "Could not reach "
                "Apicurio Registry: "
                f"{exc.reason}"
            ) from exc

        try:
            schema = json.loads(
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
                "invalid schema JSON."
            ) from exc

        if not isinstance(
            schema,
            dict,
        ):
            raise RegistryContractError(
                "Registry content must "
                "be a JSON object."
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

    metadata = self._get_json_path(
        version_path
    )

    content_id = metadata.get(
        "contentId"
    )

    global_id = metadata.get(
        "globalId"
    )

    state = metadata.get(
        "state"
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
            body = response.read()

    except HTTPError as exc:
        raise RegistryError(
            "Apicurio request failed: "
            f"GET {url} -> "
            f"HTTP {exc.code}."
        ) from exc

    except URLError as exc:
        raise RegistryError(
            "Could not reach "
            "Apicurio Registry: "
            f"{exc.reason}"
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
            "invalid JSON."
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

@dataclass(
    frozen=True,
    slots=True,
)
class RegisteredAvroContract:
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
