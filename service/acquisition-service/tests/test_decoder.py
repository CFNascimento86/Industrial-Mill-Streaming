import struct
import pytest
from acquisition_service.decoder import (
    AcquisitionDecodingError,
    decode_float32,
    decode_value,
)


def _encode_float32_big_endian(
    value: float,
) -> list[int]:
    packed = struct.pack(
        ">f",
        value,
    )

    return [
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
    ]


def test_decode_float32_big_endian():
    value = 301.42

    registers = _encode_float32_big_endian(
        value
    )

    decoded = decode_float32(
        registers=registers,
        byte_order="big_endian",
        word_order="big_endian",
    )

    assert decoded == pytest.approx(
        value,
        rel=1e-6,
    )


def test_decode_float32_little_word_order():
    value = 301.42

    registers = _encode_float32_big_endian(
        value
    )

    reversed_registers = [
        registers[1],
        registers[0],
    ]

    decoded = decode_float32(
        registers=reversed_registers,
        byte_order="big_endian",
        word_order="little_endian",
    )

    assert decoded == pytest.approx(
        value,
        rel=1e-6,
    )


def test_decode_float32_requires_two_registers():
    with pytest.raises(
        AcquisitionDecodingError,
        match="exactly two registers",
    ):
        decode_float32(
            registers=[12345],
            byte_order="big_endian",
            word_order="big_endian",
        )


def test_decode_float32_rejects_invalid_word_order():
    registers = _encode_float32_big_endian(
        100.0
    )

    with pytest.raises(
        AcquisitionDecodingError,
        match="Unsupported word order",
    ):
        decode_float32(
            registers=registers,
            byte_order="big_endian",
            word_order="invalid",
        )


def test_decode_float32_rejects_invalid_byte_order():
    registers = _encode_float32_big_endian(
        100.0
    )

    with pytest.raises(
        AcquisitionDecodingError,
        match="Unsupported byte order",
    ):
        decode_float32(
            registers=registers,
            byte_order="invalid",
            word_order="big_endian",
        )


def test_generic_decoder_supports_float32():
    registers = _encode_float32_big_endian(
        250.0
    )

    decoded = decode_value(
        data_type="FLOAT32",
        registers=registers,
        byte_order="big_endian",
        word_order="big_endian",
    )

    assert decoded == pytest.approx(
        250.0,
        rel=1e-6,
    )


def test_generic_decoder_rejects_unsupported_type():
    with pytest.raises(
        AcquisitionDecodingError,
        match="Unsupported data type",
    ):
        decode_value(
            data_type="INT64",
            registers=[0, 0],
            byte_order="big_endian",
            word_order="big_endian",
        )
