from __future__ import annotations
from dataclasses import dataclass
import struct


MAGIC_BYTE = 0x00

CONTENT_ID_MIN = 1
CONTENT_ID_MAX = 2_147_483_647

_HEADER_STRUCT = struct.Struct(
    ">Bi"
)

HEADER_SIZE = _HEADER_STRUCT.size


class ApicurioWireFormatError(
    ValueError
):
    """
    Falha relacionada ao framing Kafka
    utilizado pelo Apicurio Registry.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class ApicurioFramedPayload:
    """
    Representação de um payload Kafka
    após remoção do framing Apicurio.
    """

    content_id: int
    payload: bytes


class ApicurioWireFramer:
    """
    Aplica o framing Apicurio sobre
    um payload Avro já serializado.

    Formato:

        byte 0:
            magic byte

        bytes 1..4:
            contentId em big-endian

        bytes 5..N:
            payload Avro
    """

    def __init__(
        self,
        *,
        content_id: int,
    ) -> None:
        _validate_content_id(
            content_id
        )

        self._content_id = (
            content_id
        )

    @property
    def content_id(
        self,
    ) -> int:
        return self._content_id

    def frame(
        self,
        payload: bytes,
    ) -> bytes:
        """
        Encapsula um payload Avro
        no wire format Apicurio.
        """

        if not isinstance(
            payload,
            bytes,
        ):
            raise TypeError(
                "payload must be bytes."
            )

        header = (
            _HEADER_STRUCT.pack(
                MAGIC_BYTE,
                self._content_id,
            )
        )

        return header + payload

    @staticmethod
    def parse(
        data: bytes,
    ) -> ApicurioFramedPayload:
        """
        Remove o framing e retorna
        contentId + payload original.

        Este método existe principalmente
        para validação e futuros consumers.
        """

        if not isinstance(
            data,
            bytes,
        ):
            raise TypeError(
                "data must be bytes."
            )

        if len(data) < HEADER_SIZE:
            raise (
                ApicurioWireFormatError(
                    "Framed payload is "
                    "smaller than the "
                    "Apicurio header."
                )
            )

        (
            magic_byte,
            content_id,
        ) = _HEADER_STRUCT.unpack(
            data[:HEADER_SIZE]
        )

        if magic_byte != MAGIC_BYTE:
            raise (
                ApicurioWireFormatError(
                    "Unsupported Apicurio "
                    f"magic byte: "
                    f"{magic_byte}."
                )
            )

        _validate_content_id(
            content_id
        )

        return ApicurioFramedPayload(
            content_id=content_id,
            payload=data[
                HEADER_SIZE:
            ],
        )


def _validate_content_id(
    content_id: int,
) -> None:
    """
    Valida o intervalo utilizado
    pelo identificador de 4 bytes.
    """

    if isinstance(
        content_id,
        bool,
    ) or not isinstance(
        content_id,
        int,
    ):
        raise TypeError(
            "content_id must be an integer."
        )

    if not (
        CONTENT_ID_MIN
        <= content_id
        <= CONTENT_ID_MAX
    ):
        raise (
            ApicurioWireFormatError(
                "content_id must be between "
                f"{CONTENT_ID_MIN} and "
                f"{CONTENT_ID_MAX}."
            )
        )
