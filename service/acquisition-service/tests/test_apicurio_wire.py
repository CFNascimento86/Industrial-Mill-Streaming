import pytest
from acquisition_service.apicurio_wire import (
    ApicurioFramedPayload,
    ApicurioWireFormatError,
    ApicurioWireFramer,
    HEADER_SIZE,
)


def test_apicurio_wire_framer_frames_payload():
    framer = ApicurioWireFramer(
        content_id=17
    )

    avro_payload = (
        b"\x02\x04\x06\x08"
    )

    framed = framer.frame(
        avro_payload
    )

    assert framed == (
        b"\x00"
        b"\x00\x00\x00\x11"
        b"\x02\x04\x06\x08"
    )

    assert len(framed) == (
        HEADER_SIZE
        + len(avro_payload)
    )


def test_apicurio_wire_framer_round_trip():
    framer = ApicurioWireFramer(
        content_id=314
    )

    avro_payload = (
        b"\x10\x20\x30\x40"
    )

    framed = framer.frame(
        avro_payload
    )

    restored = (
        ApicurioWireFramer.parse(
            framed
        )
    )

    assert restored == (
        ApicurioFramedPayload(
            content_id=314,
            payload=avro_payload,
        )
    )


def test_apicurio_wire_framer_rejects_invalid_magic_byte():
    invalid = (
        b"\x01"
        b"\x00\x00\x00\x11"
        b"\x02\x04"
    )

    with pytest.raises(
        ApicurioWireFormatError,
        match="magic byte",
    ):
        ApicurioWireFramer.parse(
            invalid
        )


def test_apicurio_wire_framer_rejects_short_payload():
    with pytest.raises(
        ApicurioWireFormatError,
        match="smaller",
    ):
        ApicurioWireFramer.parse(
            b"\x00\x00"
        )


@pytest.mark.parametrize(
    "content_id",
    [
        0,
        -1,
        2_147_483_648,
    ],
)
def test_apicurio_wire_framer_rejects_invalid_content_id(
    content_id,
):
    with pytest.raises(
        ApicurioWireFormatError
    ):
        ApicurioWireFramer(
            content_id=content_id
        )
