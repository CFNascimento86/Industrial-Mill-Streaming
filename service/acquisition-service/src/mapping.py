from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml
from acquisition_service.model import (
    ReadWindow,
    VariableMapping,
)


class MappingError(ValueError):
    pass


def load_mapping(
    path: str | Path,
) -> dict[str, Any]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Mapping file '{file_path}' was not found."
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise MappingError(
            "Modbus mapping root must be a mapping."
        )

    return data


def build_variable_mappings(
    config: dict[str, Any],
) -> tuple[VariableMapping, ...]:
    variables = config.get(
        "variables"
    )

    if not isinstance(variables, list):
        raise MappingError(
            "'variables' must be a list."
        )

    mappings: list[
        VariableMapping
    ] = []

    logical_names: set[str] = set()
    occupied: set[int] = set()

    for variable in variables:
        logical_name = variable["logical_name"]
        address = variable["address"]
        data_type = variable["data_type"]

        mapping = VariableMapping(
            logical_name=logical_name,
            address=address,
            data_type=data_type,
        )

        if logical_name in logical_names:
            raise MappingError(
                f"Duplicate variable: {logical_name}"
            )

        for register_address in range(
            mapping.address,
            mapping.end_address,
        ):
            if register_address in occupied:
                raise MappingError(
                    "Overlapping Modbus register "
                    f"at address {register_address}."
                )

            occupied.add(
                register_address
            )

        logical_names.add(
            logical_name
        )

        mappings.append(
            mapping
        )

    return tuple(
        sorted(
            mappings,
            key=lambda item: item.address,
        )
    )


def build_read_windows(
    mappings: tuple[
        VariableMapping,
        ...
    ],
) -> tuple[ReadWindow, ...]:
    if not mappings:
        return ()

    windows: list[
        ReadWindow
    ] = []

    current_variables = [
        mappings[0]
    ]

    window_start = (
        mappings[0].address
    )

    window_end = (
        mappings[0].end_address
    )

    for mapping in mappings[1:]:
        if mapping.address == window_end:
            current_variables.append(
                mapping
            )

            window_end = (
                mapping.end_address
            )

            continue

        windows.append(
            ReadWindow(
                address=window_start,
                count=(
                    window_end
                    - window_start
                ),
                variables=tuple(
                    current_variables
                ),
            )
        )

        current_variables = [
            mapping
        ]

        window_start = (
            mapping.address
        )

        window_end = (
            mapping.end_address
        )

    windows.append(
        ReadWindow(
            address=window_start,
            count=(
                window_end
                - window_start
            ),
            variables=tuple(
                current_variables
            ),
        )
    )

    return tuple(windows)
