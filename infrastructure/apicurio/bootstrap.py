from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class BootstrapError(RuntimeError):
    """
    Falha durante o bootstrap do Apicurio Registry.
    """


SCRIPT_PATH = Path(__file__).resolve()

REPOSITORY_ROOT = (
    SCRIPT_PATH
    .parents[2]
)

CONFIG_PATH = (
    SCRIPT_PATH
    .with_name("bootstrap-config.json")
)


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


class RegistryClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
    ) -> None:
        self._base_url = (
            base_url.rstrip("/")
        )

        self._timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> tuple[int, str]:
        url = (
            f"{self._base_url}/"
            f"{path.lstrip('/')}"
        )

        data = None

        headers = {
            "Accept": "application/json",
        }

        if payload is not None:
            data = json.dumps(
                payload
            ).encode("utf-8")

            headers[
                "Content-Type"
            ] = "application/json"

        request = Request(
            url=url,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                body = (
                    response
                    .read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
                )

                return (
                    response.status,
                    body,
                )

        except HTTPError as exc:
            body = (
                exc
                .read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

            return (
                exc.code,
                body,
            )

        except URLError as exc:
            raise BootstrapError(
                f"Could not reach Apicurio Registry "
                f"at '{url}': {exc.reason}"
            ) from exc


def require_status(
    *,
    status: int,
    expected: tuple[int, ...],
    operation: str,
    body: str,
) -> None:
    if status in expected:
        return

    raise BootstrapError(
        f"{operation} failed. "
        f"HTTP {status}. "
        f"Response: {body}"
    )


def parse_json(
    body: str,
    *,
    operation: str,
) -> Any:
    try:
        return json.loads(body)

    except json.JSONDecodeError as exc:
        raise BootstrapError(
            f"{operation} returned invalid JSON: "
            f"{body}"
        ) from exc


def wait_for_registry(
    *,
    client: RegistryClient,
    timeout_seconds: float,
) -> None:
    print(
        "[WAIT] Waiting for Apicurio Registry..."
    )

    deadline = (
        time.monotonic()
        + timeout_seconds
    )

    while time.monotonic() < deadline:
        try:
            status, _ = client.request(
                "GET",
                "/system/info",
            )

            if status == 200:
                print(
                    "[OK]   Apicurio Registry is ready."
                )

                return

        except BootstrapError:
            pass

        time.sleep(1.0)

    raise BootstrapError(
        "Apicurio Registry did not become "
        f"available within {timeout_seconds} seconds."
    )


def ensure_group(
    *,
    client: RegistryClient,
    group_id: str,
    description: str,
) -> None:
    encoded_group_id = quote(
        group_id,
        safe="",
    )

    status, body = client.request(
        "GET",
        f"/groups/{encoded_group_id}",
    )

    if status == 200:
        print(
            f"[OK]   Group '{group_id}' already exists."
        )

        return

    if status != 404:
        require_status(
            status=status,
            expected=(200, 404),
            operation="Check group",
            body=body,
        )

    print(
        f"[CREATE] Group '{group_id}'."
    )

    status, body = client.request(
        "POST",
        "/groups",
        {
            "groupId": group_id,
            "description": description,
        },
    )

    require_status(
        status=status,
        expected=(
            200,
            201,
            204,
        ),
        operation="Create group",
        body=body,
    )

    print(
        f"[OK]   Group '{group_id}' created."
    )


def ensure_artifact(
    *,
    client: RegistryClient,
    group_id: str,
    artifact_config: dict[str, Any],
    schema_text: str,
) -> None:
    artifact_id = artifact_config["id"]
    version = artifact_config["version"]

    encoded_group_id = quote(
        group_id,
        safe="",
    )

    encoded_artifact_id = quote(
        artifact_id,
        safe="",
    )

    artifact_path = (
        f"/groups/{encoded_group_id}"
        f"/artifacts/{encoded_artifact_id}"
    )

    status, body = client.request(
        "GET",
        artifact_path,
    )

    if status == 404:
        print(
            f"[CREATE] Artifact "
            f"'{artifact_id}' version '{version}'."
        )

        payload = {
            "artifactId": artifact_id,
            "artifactType": (
                artifact_config["type"]
            ),
            "name": (
                artifact_config["name"]
            ),
            "description": (
                artifact_config["description"]
            ),
            "firstVersion": {
                "version": version,
                "content": {
                    "content": schema_text,
                    "contentType": (
                        "application/json"
                    ),
                },
            },
        }

        status, body = client.request(
            "POST",
            (
                f"/groups/{encoded_group_id}"
                "/artifacts"
            ),
            payload,
        )

        require_status(
            status=status,
            expected=(
                200,
                201,
            ),
            operation="Create artifact",
            body=body,
        )

        print(
            f"[OK]   Artifact '{artifact_id}' "
            f"version '{version}' created."
        )

    elif status == 200:
        print(
            f"[OK]   Artifact "
            f"'{artifact_id}' already exists."
        )

    else:
        require_status(
            status=status,
            expected=(200, 404),
            operation="Check artifact",
            body=body,
        )

    validate_version(
        client=client,
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        local_schema_text=schema_text,
    )


def validate_version(
    *,
    client: RegistryClient,
    group_id: str,
    artifact_id: str,
    version: str,
    local_schema_text: str,
) -> None:
    encoded_group_id = quote(
        group_id,
        safe="",
    )

    encoded_artifact_id = quote(
        artifact_id,
        safe="",
    )

    encoded_version = quote(
        version,
        safe="",
    )

    version_base = (
        f"/groups/{encoded_group_id}"
        f"/artifacts/{encoded_artifact_id}"
        f"/versions/{encoded_version}"
    )

    status, body = client.request(
        "GET",
        version_base,
    )

    if status == 404:
        raise BootstrapError(
            f"Artifact '{artifact_id}' exists, "
            f"but required version '{version}' "
            "does not exist. "
            "This is considered Registry drift."
        )

    require_status(
        status=status,
        expected=(200,),
        operation="Validate artifact version",
        body=body,
    )

    status, registered_schema_text = (
        client.request(
            "GET",
            f"{version_base}/content",
        )
    )

    require_status(
        status=status,
        expected=(200,),
        operation="Retrieve registered schema",
        body=registered_schema_text,
    )

    try:
        local_schema = json.loads(
            local_schema_text
        )

        registered_schema = json.loads(
            registered_schema_text
        )

    except json.JSONDecodeError as exc:
        raise BootstrapError(
            "Could not compare local and "
            "registered Avro schemas."
        ) from exc

    if registered_schema != local_schema:
        raise BootstrapError(
            f"Schema drift detected for "
            f"'{artifact_id}' version '{version}'. "
            "The registered schema differs from "
            "the contract stored in Git."
        )

    print(
        f"[OK]   Artifact version '{version}' "
        "matches the local contract."
    )


def ensure_rule(
    *,
    client: RegistryClient,
    group_id: str,
    artifact_id: str,
    rule_type: str,
    expected_config: str,
) -> None:
    encoded_group_id = quote(
        group_id,
        safe="",
    )

    encoded_artifact_id = quote(
        artifact_id,
        safe="",
    )

    encoded_rule_type = quote(
        rule_type,
        safe="",
    )

    rules_base = (
        f"/groups/{encoded_group_id}"
        f"/artifacts/{encoded_artifact_id}"
        "/rules"
    )

    status, body = client.request(
        "GET",
        f"{rules_base}/{encoded_rule_type}",
    )

    if status == 200:
        rule = parse_json(
            body,
            operation=(
                f"Read rule {rule_type}"
            ),
        )

        actual_config = rule.get(
            "config"
        )

        if actual_config != expected_config:
            raise BootstrapError(
                f"Rule drift detected: "
                f"{rule_type} expected "
                f"'{expected_config}', "
                f"but Registry contains "
                f"'{actual_config}'."
            )

        print(
            f"[OK]   Rule {rule_type}="
            f"{expected_config} already exists."
        )

        return

    if status != 404:
        require_status(
            status=status,
            expected=(200, 404),
            operation=(
                f"Check rule {rule_type}"
            ),
            body=body,
        )

    print(
        f"[CREATE] Rule "
        f"{rule_type}={expected_config}."
    )

    status, body = client.request(
        "POST",
        rules_base,
        {
            "ruleType": rule_type,
            "config": expected_config,
        },
    )

    require_status(
        status=status,
        expected=(204,),
        operation=(
            f"Create rule {rule_type}"
        ),
        body=body,
    )

    print(
        f"[OK]   Rule "
        f"{rule_type}={expected_config} created."
    )


def bootstrap() -> None:
    config = load_config()

    configured_base_url = (
        config["registry_base_url"]
    )

    registry_base_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        configured_base_url,
    )

    timeout_seconds = float(
        os.getenv(
            "APICURIO_BOOTSTRAP_TIMEOUT_SECONDS",
            "30",
        )
    )

    client = RegistryClient(
        registry_base_url
    )

    wait_for_registry(
        client=client,
        timeout_seconds=timeout_seconds,
    )

    group = config["group"]
    artifact = config["artifact"]

    schema_path = (
        REPOSITORY_ROOT
        / artifact["schema_path"]
    )

    if not schema_path.exists():
        raise BootstrapError(
            f"Schema file was not found: "
            f"{schema_path}"
        )

    schema_text = schema_path.read_text(
        encoding="utf-8"
    )

    # Valida JSON local antes de qualquer alteração
    # no Registry.
    try:
        json.loads(schema_text)

    except json.JSONDecodeError as exc:
        raise BootstrapError(
            f"Local Avro schema is not "
            f"valid JSON: {schema_path}"
        ) from exc

    ensure_group(
        client=client,
        group_id=group["id"],
        description=group["description"],
    )

    ensure_artifact(
        client=client,
        group_id=group["id"],
        artifact_config=artifact,
        schema_text=schema_text,
    )

    for rule in config["rules"]:
        ensure_rule(
            client=client,
            group_id=group["id"],
            artifact_id=artifact["id"],
            rule_type=rule["type"],
            expected_config=(
                rule["config"]
            ),
        )

    print()
    print(
        "[SUCCESS] Apicurio Registry "
        "bootstrap completed."
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
