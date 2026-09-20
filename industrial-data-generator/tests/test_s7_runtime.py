import struct
import pytest

from s7.factory import (
    build_s7_reference_model,
)
from s7.runtime import S7Runtime


def test_cane_flow_is_written_to_db100_offset_28(
    reference_s7_config,
    engine,
):
    model = build_s7_reference_model(
        reference_s7_config
    )

    runtime = S7Runtime(
        model=model
    )

    snapshot = engine.snapshot()

    runtime.write_snapshot(
        snapshot
    )

    encoded = runtime.read_area(
        db_number=100,
        byte_offset=28,
        size_bytes=4,
    )

    expected = struct.pack(
        ">f",
        snapshot["cane_flow"],
    )

    assert encoded == expected


def test_runtime_rejects_incomplete_snapshot(
    reference_s7_config,
    engine,
):
    model = build_s7_reference_model(
        reference_s7_config
    )

    runtime = S7Runtime(
        model=model
    )

    snapshot = engine.snapshot()

    del snapshot[
        "cane_flow"
    ]

    with pytest.raises(
        KeyError
    ):
        runtime.write_snapshot(
            snapshot
        )
