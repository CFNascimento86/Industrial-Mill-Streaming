from __future__ import annotations
from typing import Any
from config.loader import ConfigurationError
from .model import (
    S7DataBlock,
    S7ReferenceModel,
    S7Variable,
    S7_TYPE_SIZES,
)


def build_s7_reference_model(
    config: dict[str, Any],
) -> S7ReferenceModel:
    """
    Constrói e valida o modelo S7 da Reference Plant.
    """
    model_config = config["model"]

    try:
        name = str(
            model_config["name"]
        )

        version = str(
            model_config["version"]
        )
    except KeyError as exc:
        raise ConfigurationError(
            "Reference S7 model must define "
            "'name' and 'version'."
        ) from exc

    data_blocks: list[S7DataBlock] = []

    db_numbers: set[int] = set()
    db_names: set[str] = set()
    mapped_variables: set[str] = set()

    for db_config in config["data_blocks"]:
        data_block = _build_data_block(
            db_config=db_config,
            db_numbers=db_numbers,
            db_names=db_names,
            mapped_variables=mapped_variables,
        )

        data_blocks.append(
            data_block
        )

    return S7ReferenceModel(
        name=name,
        version=version,
        data_blocks=tuple(data_blocks),
    )


def _build_data_block(
    *,
    db_config: dict[str, Any],
    db_numbers: set[int],
    db_names: set[str],
    mapped_variables: set[str],
) -> S7DataBlock:
    """
    Constrói e valida um Data Block.
    """
    try:
        db_number = int(
            db_config["db_number"]
        )

        logical_name = str(
            db_config["logical_name"]
        )

        size_bytes = int(
            db_config["size_bytes"]
        )

        variable_configs = db_config[
            "variables"
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(
            "Invalid S7 data block definition."
        ) from exc

    if db_number <= 0:
        raise ConfigurationError(
            "S7 DB number must be greater than zero."
        )

    if db_number in db_numbers:
        raise ConfigurationError(
            f"DB{db_number} is defined more than once."
        )

    if logical_name in db_names:
        raise ConfigurationError(
            f"S7 data block logical name "
            f"'{logical_name}' is duplicated."
        )

    if size_bytes <= 0:
        raise ConfigurationError(
            f"DB{db_number} size must be greater than zero."
        )

    if not isinstance(
        variable_configs,
        list,
    ):
        raise ConfigurationError(
            f"'variables' in DB{db_number} must be a list."
        )

    variables: list[S7Variable] = []

    occupied_bytes: set[int] = set()

    for variable_config in variable_configs:
        variable = _build_variable(
            db_number=db_number,
            db_size=size_bytes,
            config=variable_config,
            mapped_variables=mapped_variables,
            occupied_bytes=occupied_bytes,
        )

        variables.append(
            variable
        )

    db_numbers.add(
        db_number
    )

    db_names.add(
        logical_name
    )

    return S7DataBlock(
        db_number=db_number,
        logical_name=logical_name,
        size_bytes=size_bytes,
        variables=tuple(variables),
    )


def _build_variable(
    *,
    db_number: int,
    db_size: int,
    config: dict[str, Any],
    mapped_variables: set[str],
    occupied_bytes: set[int],
) -> S7Variable:
    """
    Constrói e valida um mapeamento de variável S7.
    """
    try:
        logical_name = str(
            config["variable"]
        )

        data_type = str(
            config["data_type"]
        ).upper()

        byte_offset = int(
            config["byte_offset"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(
            f"Invalid variable definition in DB{db_number}."
        ) from exc

    if logical_name in mapped_variables:
        raise ConfigurationError(
            f"Variable '{logical_name}' is mapped more than once."
        )

    if data_type not in S7_TYPE_SIZES:
        raise ConfigurationError(
            f"Unsupported S7 data type '{data_type}' "
            f"for variable '{logical_name}'."
        )

    if byte_offset < 0:
        raise ConfigurationError(
            f"Variable '{logical_name}' has a negative byte offset."
        )

    size_bytes = S7_TYPE_SIZES[
        data_type
    ]

    end_offset = (
        byte_offset
        + size_bytes
    )

    if end_offset > db_size:
        raise ConfigurationError(
            f"Variable '{logical_name}' exceeds "
            f"DB{db_number} size."
        )

    variable_bytes = set(
        range(
            byte_offset,
            end_offset,
        )
    )

    overlap = (
        variable_bytes
        & occupied_bytes
    )

    if overlap:
        raise ConfigurationError(
            f"Variable '{logical_name}' overlaps another "
            f"mapping in DB{db_number}."
        )

    occupied_bytes.update(
        variable_bytes
    )

    mapped_variables.add(
        logical_name
    )

    return S7Variable(
        logical_name=logical_name,
        data_type=data_type,
        byte_offset=byte_offset,
    )
  
