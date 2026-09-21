from typing import Any
from config.loader import ConfigurationError
from modbus.model import (
    MODBUS_TYPE_REGISTER_COUNTS,
    ModbusEncoding,
    ModbusReferenceModel,
    ModbusRegister,
)


SUPPORTED_BYTE_ORDERS = {"big_endian", "little_endian"}
SUPPORTED_WORD_ORDERS = {"big_endian", "little_endian"}


def build_modbus_reference_model(
    config: dict[str, Any],
) -> ModbusReferenceModel:
    """
    Constrói o modelo Modbus validado a partir da configuração carregada.
    """

    model_config = config["model"]
    protocol_config = config["protocol"]
    encoding_config = config["encoding"]

    name = _require_string(model_config, "name", "model")
    version = _require_string(model_config, "version", "model")
    process = _require_string(model_config, "process", "model")

    protocol_name = _require_string(
        protocol_config,
        "name",
        "protocol",
    )

    if protocol_name != "modbus_tcp":
        raise ConfigurationError(
            f"Unsupported Modbus protocol: {protocol_name}"
        )

    addressing = _require_string(
        protocol_config,
        "addressing",
        "protocol",
    )

    if addressing != "zero_based":
        raise ConfigurationError(
            "IMS Reference Modbus Model requires zero-based addressing."
        )

    register_type = _require_string(
        protocol_config,
        "register_type",
        "protocol",
    )

    if register_type != "holding_register":
        raise ConfigurationError(
            "IMS Reference Modbus Model currently supports only "
            "'holding_register'."
        )

    encoding = _build_encoding(encoding_config)

    registers = tuple(
        _build_register(register_config)
        for register_config in config["registers"]
    )

    _validate_register_map(registers)

    return ModbusReferenceModel(
        name=name,
        version=version,
        process=process,
        addressing=addressing,
        register_type=register_type,
        encoding=encoding,
        registers=registers,
    )


def _build_encoding(
    config: dict[str, Any],
) -> ModbusEncoding:
    float32_config = config.get("float32")

    if not isinstance(float32_config, dict):
        raise ConfigurationError(
            "'encoding.float32' must be a mapping."
        )

    register_count = float32_config.get("register_count")

    if register_count != MODBUS_TYPE_REGISTER_COUNTS["FLOAT32"]:
        raise ConfigurationError(
            "FLOAT32 must occupy exactly 2 Modbus registers."
        )

    byte_order = _require_string(
        float32_config,
        "byte_order",
        "encoding.float32",
    )

    word_order = _require_string(
        float32_config,
        "word_order",
        "encoding.float32",
    )

    if byte_order not in SUPPORTED_BYTE_ORDERS:
        raise ConfigurationError(
            f"Unsupported byte order: {byte_order}"
        )

    if word_order not in SUPPORTED_WORD_ORDERS:
        raise ConfigurationError(
            f"Unsupported word order: {word_order}"
        )

    return ModbusEncoding(
        byte_order=byte_order,
        word_order=word_order,
    )


def _build_register(
    config: dict[str, Any],
) -> ModbusRegister:
    if not isinstance(config, dict):
        raise ConfigurationError(
            "Each Modbus register definition must be a mapping."
        )

    logical_name = _require_string(
        config,
        "logical_name",
        "register",
    )

    data_type = _require_string(
        config,
        "data_type",
        f"register '{logical_name}'",
    )

    if data_type not in MODBUS_TYPE_REGISTER_COUNTS:
        raise ConfigurationError(
            f"Unsupported Modbus data type '{data_type}' "
            f"for variable '{logical_name}'."
        )

    address = config.get("address")

    if not isinstance(address, int) or isinstance(address, bool):
        raise ConfigurationError(
            f"Address for '{logical_name}' must be an integer."
        )

    if address < 0:
        raise ConfigurationError(
            f"Address for '{logical_name}' cannot be negative."
        )

    return ModbusRegister(
        logical_name=logical_name,
        address=address,
        data_type=data_type,
    )


def _validate_register_map(
    registers: tuple[ModbusRegister, ...],
) -> None:
    logical_names: set[str] = set()
    occupied_addresses: dict[int, str] = {}

    for register in registers:
        if register.logical_name in logical_names:
            raise ConfigurationError(
                f"Duplicate Modbus variable: {register.logical_name}"
            )

        logical_names.add(register.logical_name)

        for address in range(
            register.address,
            register.end_address,
        ):
            previous = occupied_addresses.get(address)

            if previous is not None:
                raise ConfigurationError(
                    f"Modbus register overlap at address {address}: "
                    f"'{register.logical_name}' conflicts with "
                    f"'{previous}'."
                )

            occupied_addresses[address] = register.logical_name


def _require_string(
    config: dict[str, Any],
    key: str,
    section: str,
) -> str:
    value = config.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(
            f"'{key}' in {section} must be a non-empty string."
        )

    return value
