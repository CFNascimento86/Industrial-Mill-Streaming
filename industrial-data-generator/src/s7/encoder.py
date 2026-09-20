from __future__ import annotations
import struct


class S7EncodingError(ValueError):
    """
    Erro durante codificação de um valor para representação S7.
    """


def encode_s7_value(
    *,
    data_type: str,
    value: float,
) -> bytes:
    """
    Codifica um valor Python para sua representação binária S7.
    """
    normalized_type = (
        data_type.upper()
    )

    if normalized_type == "REAL":
        return encode_real(
            value
        )

    raise S7EncodingError(
        f"Unsupported S7 data type '{data_type}'."
    )


def encode_real(
    value: float,
) -> bytes:
    """
    Codifica um valor como Siemens S7 REAL.
    REAL utiliza IEEE 754 binary32 em ordem big-endian.
    """
    try:
        return struct.pack(
            ">f",
            float(value),
        )
    except (
        TypeError,
        ValueError,
        OverflowError,
        struct.error,
    ) as exc:
        raise S7EncodingError(
            f"Cannot encode '{value}' as S7 REAL."
        ) from exc
      
