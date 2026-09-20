import struct
import pytest

from s7.encoder import (
    S7EncodingError,
    encode_real,
    encode_s7_value,
)


def test_real_uses_four_bytes():
    encoded = encode_real(
        300.0
    )

    assert len(encoded) == 4


def test_real_uses_big_endian_ieee754():
    encoded = encode_real(
        300.0
    )

    expected = struct.pack(
        ">f",
        300.0,
    )

    assert encoded == expected


def test_generic_encoder_supports_real():
    encoded = encode_s7_value(
        data_type="REAL",
        value=123.45,
    )

    assert encoded == struct.pack(
        ">f",
        123.45,
    )


def test_unsupported_type_is_rejected():
    with pytest.raises(
        S7EncodingError
    ):
        encode_s7_value(
            data_type="UNKNOWN",
            value=10,
        )
      
