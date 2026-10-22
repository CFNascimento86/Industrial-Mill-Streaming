from __future__ import annotations
from dataclasses import dataclass
import struct


MAGIC_BYTE = 0x00

_HEADER_STRUCT = struct.Struct(
    ">Bi"
)

HEADER_SIZE = (
    _HEADER_STRUCT.size
)


class ApicurioWireFormatError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class ApicurioFramedPayload:
    content_id: int
    payload: bytes


def parse_apicurio_payload(
    data: bytes,
) -> ApicurioFramedPayload:
    if not isinstance(
        data,
        bytes,
    ):
        raise TypeError(
            "data must be bytes."
        )

    if len(data) < HEADER_SIZE:
        raise ApicurioWireFormatError(
            "Payload is smaller than "
            "the Apicurio header."
        )

    (
        magic_byte,
        content_id,
    ) = _HEADER_STRUCT.unpack(
        data[:HEADER_SIZE]
    )

    if magic_byte != MAGIC_BYTE:
        raise ApicurioWireFormatError(
            "Unsupported Apicurio "
            f"magic byte: {magic_byte}."
        )

    if content_id <= 0:
        raise ApicurioWireFormatError(
            "content_id must be positive."
        )

    return ApicurioFramedPayload(
        content_id=content_id,
        payload=data[
            HEADER_SIZE:
        ],
    )
