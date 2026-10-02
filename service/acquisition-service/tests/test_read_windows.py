from acquisition_service.mapping import (
    build_read_windows,
    build_variable_mappings,
)


def test_reference_mapping_generates_five_read_windows(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    assert len(windows) == 5


def test_reference_read_windows_are_correct(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    actual = [
        (
            window.address,
            window.count,
        )
        for window in windows
    ]

    expected = [
        (0, 16),
        (100, 8),
        (200, 6),
        (300, 6),
        (400, 2),
    ]

    assert actual == expected


def test_first_window_contains_feed_preparation_variables(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    first_window = windows[0]

    logical_names = [
        variable.logical_name
        for variable in first_window.variables
    ]

    assert logical_names == [
        "feed_conveyor_speed",
        "feed_conveyor_motor_current",
        "chopper_speed",
        "chopper_motor_current",
        "shredder_speed",
        "shredder_motor_current",
        "shredder_vibration_rms",
        "cane_flow",
    ]


def test_last_window_contains_bagasse_moisture(
    modbus_mapping_config,
):
    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    last_window = windows[-1]

    assert last_window.address == 400
    assert last_window.count == 2

    assert [
        variable.logical_name
        for variable in last_window.variables
    ] == [
        "bagasse_moisture"
    ]


def test_empty_mapping_generates_no_windows():
    windows = build_read_windows(
        ()
    )

    assert windows == ()
