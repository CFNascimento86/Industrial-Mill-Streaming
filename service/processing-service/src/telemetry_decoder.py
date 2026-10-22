from __future__ import annotations

from processing_service.apicurio_wire import (
    parse_apicurio_payload,
)
from processing_service.avro_codec import (
    TelemetryAvroDecoder,
)
from processing_service.contract import (
    TelemetryObservation,
)
from processing_service.registry_client import (
    ApicurioRegistryClient,
)


class TelemetryMessageDecoder:
    def __init__(
        self,
        *,
        registry_client: (
            ApicurioRegistryClient
        ),
    ) -> None:
        self._registry_client = (
            registry_client
        )

        self._codecs: dict[
            int,
            TelemetryAvroDecoder,
        ] = {}

    def decode(
        self,
        value: bytes,
    ) -> TelemetryObservation:
        framed = (
            parse_apicurio_payload(
                value
            )
        )

        codec = self._codecs.get(
            framed.content_id
        )

        if codec is None:
            schema = (
                self._registry_client
                .resolve_avro_schema_by_content_id(
                    framed.content_id
                )
            )

            codec = (
                TelemetryAvroDecoder(
                    schema
                )
            )

            self._codecs[
                framed.content_id
            ] = codec

        return codec.deserialize(
            framed.payload
        )
