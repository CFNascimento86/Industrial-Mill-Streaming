from __future__ import annotations
import math
import os
from datetime import timedelta
import pytest
from acquisition_service.client import (
    ModbusAcquisitionClient,
)
from acquisition_service.mapping import (
    build_read_windows,
    build_variable_mappings,
)


RUN_INTEGRATION_TESTS = (
    os.getenv(
        "RUN_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_INTEGRATION_TESTS,
        reason=(
            "Integration tests require "
            "RUN_INTEGRATION_TESTS=1."
        ),
    ),
]


EXPECTED_VARIABLES = {
    "feed_conveyor_speed",
    "feed_conveyor_motor_current",
    "chopper_speed",
    "chopper_motor_current",
    "shredder_speed",
    "shredder_motor_current",
    "shredder_vibration_rms",
    "cane_flow",
    "mill_01_upper_roll_speed",
    "mill_01_hydraulic_pressure",
    "mill_01_lubrication_oil_pressure",
    "mill_01_lubrication_oil_temperature",
    "main_drive_01_torque",
    "turbine_oil_pressure",
    "turbine_oil_temperature",
    "imbibition_water_flow",
    "juice_flow",
    "juice_temperature",
    "bagasse_moisture",
}


def _build_client(
    modbus_mapping_config,
) -> ModbusAcquisitionClient:
    encoding = (
        modbus_mapping_config[
            "encoding"
        ]["float32"]
    )

    return ModbusAcquisitionClient(
        host=os.getenv(
            "MODBUS_HOST",
            "127.0.0.1",
        ),
        port=int(
            os.getenv(
                "MODBUS_PORT",
                "1502",
            )
        ),
        device_id=int(
            os.getenv(
                "MODBUS_DEVICE_ID",
                "1",
            )
        ),
        byte_order=encoding[
            "byte_order"
        ],
        word_order=encoding[
            "word_order"
        ],
        timeout=3.0,
    )


def test_reference_plant_acquires_all_variables(
    modbus_mapping_config,
):
    """
    Valida a aquisição black-box completa da
    IMS Reference Plant via Modbus TCP.
    """

    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    # O Register Map atual deve resultar
    # em cinco requisições Modbus contíguas.
    assert len(windows) == 5

    client = _build_client(
        modbus_mapping_config
    )

    readings = []

    try:
        client.connect()

        for window in windows:
            readings.extend(
                client.read_window(
                    window
                )
            )

    finally:
        client.close()

    # ---------------------------------------------------------
    # Completeness
    # ---------------------------------------------------------

    assert len(readings) == 19

    logical_names = {
        reading.logical_name
        for reading in readings
    }

    assert logical_names == EXPECTED_VARIABLES

    assert len(logical_names) == len(
        readings
    )

    # ---------------------------------------------------------
    # Values
    # ---------------------------------------------------------

    assert all(
        math.isfinite(
            reading.value
        )
        for reading in readings
    )

    # ---------------------------------------------------------
    # Quality
    # ---------------------------------------------------------

    assert all(
        reading.quality == "UNKNOWN"
        for reading in readings
    )

    # ---------------------------------------------------------
    # Industrial time
    # ---------------------------------------------------------

    assert all(
        reading.observed_at.tzinfo
        is not None
        for reading in readings
    )

    assert all(
        reading.observed_at.utcoffset()
        == timedelta(0)
        for reading in readings
    )
