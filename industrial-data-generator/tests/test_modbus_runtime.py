import struct
import pytest
from modbus.factory import build_modbus_reference_model
from modbus.runtime import ModbusRuntime
from config.loader import ConfigurationError


def _expected_float32_registers(
    value: float,
) -> tuple[int, int]:
    """
    Retorna a representação esperada de um FLOAT32
    big-endian / big-word-endian.
    """
    packed = struct.pack(">f", value)

    return (
        int.from_bytes(
            packed[0:2],
            byteorder="big",
            signed=False,
        ),
        int.from_bytes(
            packed[2:4],
            byteorder="big",
            signed=False,
        ),
    )


def test_runtime_allocates_expected_register_space(
    reference_modbus_config,
):
    model = build_modbus_reference_model(
        reference_modbus_config
    )

    runtime = ModbusRuntime(model)

    # bagasse_moisture começa em HR[400]
    # e FLOAT32 ocupa HR[400] e HR[401].
    assert runtime.size == 402


def test_runtime_writes_cane_flow_to_expected_registers(
    reference_modbus_config,
):
    model = build_modbus_reference_model(
        reference_modbus_config
    )

    runtime = ModbusRuntime(model)

    snapshot = {
        register.logical_name: 0.0
        for register in model.registers
    }

    snapshot["cane_flow"] = 301.42

    runtime.write_snapshot(snapshot)

    actual = runtime.read_registers(
        address=14,
        count=2,
    )

    expected = _expected_float32_registers(
        301.42
    )

    assert actual == expected


def test_runtime_materializes_multiple_variables(
    reference_modbus_config,
):
    model = build_modbus_reference_model(
        reference_modbus_config
    )

    runtime = ModbusRuntime(model)

    snapshot = {
        register.logical_name: 0.0
        for register in model.registers
    }

    snapshot["cane_flow"] = 300.0
    snapshot["main_drive_01_torque"] = 60.0
    snapshot["bagasse_moisture"] = 50.0

    runtime.write_snapshot(snapshot)

    assert runtime.read_registers(
        address=14,
        count=2,
    ) == _expected_float32_registers(300.0)

    assert runtime.read_registers(
        address=200,
        count=2,
    ) == _expected_float32_registers(60.0)

    assert runtime.read_registers(
        address=400,
        count=2,
    ) == _expected_float32_registers(50.0)


def test_runtime_rejects_incomplete_snapshot(
    reference_modbus_config,
):
    model = build_modbus_reference_model(
        reference_modbus_config
    )

    runtime = ModbusRuntime(model)

    snapshot = {
        register.logical_name: 0.0
        for register in model.registers
    }

    del snapshot["cane_flow"]

    with pytest.raises(
        KeyError,
        match="cane_flow",
    ):
        runtime.write_snapshot(snapshot)


def test_runtime_does_not_partially_commit_invalid_snapshot(
    reference_modbus_config,
):
    model = build_modbus_reference_model(
        reference_modbus_config
    )

    runtime = ModbusRuntime(model)

    valid_snapshot = {
        register.logical_name: 10.0
        for register in model.registers
    }

    runtime.write_snapshot(valid_snapshot)

    before = runtime.read_registers(
        address=0,
        count=runtime.size,
    )

    invalid_snapshot = {
        register.logical_name: 20.0
        for register in model.registers
    }

    del invalid_snapshot["juice_temperature"]

    with pytest.raises(KeyError):
        runtime.write_snapshot(invalid_snapshot)

    after = runtime.read_registers(
        address=0,
        count=runtime.size,
    )

    assert after == before


def test_runtime_rejects_out_of_bounds_read(
    reference_modbus_config,
):
    model = build_modbus_reference_model(
        reference_modbus_config
    )

    runtime = ModbusRuntime(model)

    with pytest.raises(
        ValueError,
        match="outside",
    ):
        runtime.read_registers(
            address=401,
            count=2,
        )


def test_runtime_rejects_negative_address(
    reference_modbus_config,
):
    model = build_modbus_reference_model(
        reference_modbus_config
    )

    runtime = ModbusRuntime(model)

    with pytest.raises(
        ValueError,
        match="negative",
    ):
        runtime.read_registers(
            address=-1,
            count=1,
        )

  def test_factory_rejects_register_overlap(
    reference_modbus_config,
):
    config = {
        **reference_modbus_config,
        "registers": [
            {
                "logical_name": "variable_a",
                "address": 10,
                "data_type": "FLOAT32",
            },
            {
                "logical_name": "variable_b",
                "address": 11,
                "data_type": "FLOAT32",
            },
        ],
    }

    with pytest.raises(
        Exception,
        match="overlap",
    ):
        build_modbus_reference_model(config)
