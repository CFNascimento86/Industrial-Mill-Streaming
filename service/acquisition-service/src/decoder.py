from __future__ import annotations
import struct


class AcquisitionDecodingError(ValueError):
    pass


def decode_value(
    *,
    data_type: str,
    registers: list[int],
    byte_order: str,
    word_order: str,
) -> float:
    if data_type == "FLOAT32":
        return decode_float32(
            registers=registers,
            byte_order=byte_order,
            word_order=word_order,
        )

    raise AcquisitionDecodingError(
        f"Unsupported data type: {data_type}"
    )


def decode_float32(
    *,
    registers: list[int],
    byte_order: str,
    word_order: str,
) -> float:
    if len(registers) != 2:
        raise AcquisitionDecodingError(
            "FLOAT32 requires exactly two registers."
        )

    words = list(registers)

    if word_order == "little_endian":
        words.reverse()
    elif word_order != "big_endian":
        raise AcquisitionDecodingError(
            f"Unsupported word order: {word_order}"
        )

    raw = b"".join(
        word.to_bytes(
            2,
            byteorder="big",
            signed=False,
        )
        for word in words
    )

    if byte_order == "big_endian":
        return struct.unpack(
            ">f",
            raw,
        )[0]

    if byte_order == "little_endian":
        swapped = bytes(
            (
                raw[1],
                raw[0],
                raw[3],
                raw[2],
            )
        )

        return struct.unpack(
            ">f",
            swapped,
        )[0]

    raise AcquisitionDecodingError(
        f"Unsupported byte order: {byte_order}"
    )
