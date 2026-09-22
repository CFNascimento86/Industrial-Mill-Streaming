import struct
import pytest

from modbus.encoder import (
    ModbusEncodingError,
    encode_float32,
    encode_modbus_value,
)
from modbus.model import ModbusEncoding


def test_float32_encodes_to_two_registers():
    encoding = ModbusEncoding(
        byte_order="big_endian",
        word_order="big_endian",
    )

    registers = encode_float32(
        value=301.42,
        encoding=encoding,
    )

    assert len(registers) == 2

    assert all(
        0 <= register <= 0xFFFF
        for register in registers
    )


def test_float32_uses_big_endian_ieee754_encoding():
    encoding = ModbusEncoding(
        byte_order="big_endian",
        word_order="big_endian",
    )

    value = 301.42

    registers = encode_float32(
        value=value,
        encoding=encoding,
    )

    packed = struct.pack(">f", value)

    expected = (
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

    assert registers == expected


def test_float32_supports_little_endian_word_order():
    big_word_encoding = ModbusEncoding(
        byte_order="big_endian",
        word_order="big_endian",
    )

    little_word_encoding = ModbusEncoding(
        byte_order="big_endian",
        word_order="little_endian",
    )

    value = 301.42

    big_word_registers = encode_float32(
        value=value,
        encoding=big_word_encoding,
    )

    little_word_registers = encode_float32(
        value=value,
        encoding=little_word_encoding,
    )

    assert little_word_registers == (
        big_word_registers[1],
        big_word_registers[0],
    )


def test_generic_encoder_supports_float32():
    encoding = ModbusEncoding(
        byte_order="big_endian",
        word_order="big_endian",
    )

    direct = encode_float32(
        value=301.42,
        encoding=encoding,
    )

    generic = encode_modbus_value(
        data_type="FLOAT32",
        value=301.42,
        encoding=encoding,
    )

    assert generic == direct


def test_generic_encoder_rejects_unsupported_type():
    encoding = ModbusEncoding(
        byte_order="big_endian",
        word_order="big_endian",
    )

    with pytest.raises(
        ModbusEncodingError,
        match="Unsupported Modbus data type",
    ):
        encode_modbus_value(
            data_type="INT64",
            value=100,
            encoding=encoding,
        )
