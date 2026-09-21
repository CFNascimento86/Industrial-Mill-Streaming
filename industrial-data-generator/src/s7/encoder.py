import struct
from modbus.model import ModbusEncoding


class ModbusEncodingError(ValueError):
    pass


def encode_modbus_value(
    data_type: str,
    value: float,
    encoding: ModbusEncoding,
) -> tuple[int, ...]:
    """
    Codifica um valor Python para registradores Modbus.
    """

    if data_type == "FLOAT32":
        return encode_float32(value, encoding)

    raise ModbusEncodingError(
        f"Unsupported Modbus data type: {data_type}"
    )


def encode_float32(
    value: float,
    encoding: ModbusEncoding,
) -> tuple[int, int]:
    """
    Codifica FLOAT32 IEEE-754 em dois registradores Modbus de 16 bits.
    """

    try:
        byte_order_prefix = {
            "big_endian": ">",
            "little_endian": "<",
        }[encoding.byte_order]
    except KeyError as exc:
        raise ModbusEncodingError(
            f"Unsupported byte order: {encoding.byte_order}"
        ) from exc

    packed = struct.pack(
        f"{byte_order_prefix}f",
        float(value),
    )

    first_word = packed[0:2]
    second_word = packed[2:4]

    if encoding.word_order == "little_endian":
        first_word, second_word = second_word, first_word
    elif encoding.word_order != "big_endian":
        raise ModbusEncodingError(
            f"Unsupported word order: {encoding.word_order}"
        )

    register_1 = int.from_bytes(
        first_word,
        byteorder="big",
        signed=False,
    )

    register_2 = int.from_bytes(
        second_word,
        byteorder="big",
        signed=False,
    )

    return register_1, register_2
