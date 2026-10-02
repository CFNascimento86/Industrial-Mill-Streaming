import pytest
from acquisition_service.mapping import (
    MappingError,
    build_variable_mappings,
)


def test_mapping_builds_all_reference_variables(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    assert len(mappings) == 19


def test_mapping_is_sorted_by_address(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    addresses = [
        mapping.address
        for mapping in mappings
    ]

    assert addresses == sorted(addresses)


def test_cane_flow_mapping_is_correct(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    cane_flow = next(
        mapping
        for mapping in mappings
        if mapping.logical_name == "cane_flow"
    )

    assert cane_flow.address == 14
    assert cane_flow.data_type == "FLOAT32"
    assert cane_flow.register_count == 2
    assert cane_flow.end_address == 16


def test_mapping_rejects_duplicate_variable(
    modbus_mapping_config,
):
    config = {
        **modbus_mapping_config,
        "variables": [
            {
                "logical_name": "variable_a",
                "address": 0,
                "data_type": "FLOAT32",
            },
            {
                "logical_name": "variable_a",
                "address": 2,
                "data_type": "FLOAT32",
            },
        ],
    }

    with pytest.raises(
        MappingError,
        match="Duplicate variable",
    ):
        build_variable_mappings(
            config
        )


def test_mapping_rejects_register_overlap(
    modbus_mapping_config,
):
    config = {
        **modbus_mapping_config,
        "variables": [
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
        MappingError,
        match="Overlapping Modbus register",
    ):
        build_variable_mappings(
            config
        )


def test_mapping_rejects_missing_variable_list(
    modbus_mapping_config,
):
    config = {
        key: value
        for key, value
        in modbus_mapping_config.items()
        if key != "variables"
    }

    with pytest.raises(
        MappingError,
        match="'variables' must be a list",
    ):
        build_variable_mappings(
            config
        )
