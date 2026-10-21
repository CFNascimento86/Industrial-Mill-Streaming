from __future__ import annotations
import os
import time
from uuid import uuid4
import pytest

from confluent_kafka import (
    Consumer,
    TopicPartition,
)

from acquisition_service.apicurio_wire import (
    ApicurioWireFramer,
)
from acquisition_service.avro_codec import (
    TelemetryAvroCodec,
)
from acquisition_service.client import (
    ModbusAcquisitionClient,
)
from acquisition_service.kafka_producer import (
    DEFAULT_TELEMETRY_TOPIC,
    KafkaTelemetryProducer,
)
from acquisition_service.mapping import (
    build_read_windows,
    build_variable_mappings,
)
from acquisition_service.postgres_identity import (
    PostgresIdentityResolver,
)
from acquisition_service.registry_client import (
    ApicurioRegistryClient,
)
from acquisition_service.runtime import (
    acquire_cycle,
)
from acquisition_service.transformer import (
    TelemetryTransformer,
)


RUN_EVENT_PIPELINE_TESTS = (
    os.getenv(
        "RUN_EVENT_PIPELINE_INTEGRATION_TESTS",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not RUN_EVENT_PIPELINE_TESTS,
        reason=(
            "Event pipeline integration test "
            "requires "
            "RUN_EVENT_PIPELINE_INTEGRATION_TESTS=1."
        ),
    ),
]


EXPECTED_VARIABLE_COUNT = 19


def test_complete_event_pipeline_to_kafka(
    modbus_mapping_config,
):
    # ---------------------------------------------------------
    # Runtime configuration
    # ---------------------------------------------------------

    database_url = os.environ[
        "DATABASE_URL"
    ]

    registry_url = os.getenv(
        "APICURIO_REGISTRY_URL",
        "http://localhost:8080/apis/registry/v3",
    )

    kafka_bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )

    kafka_topic = os.getenv(
        "KAFKA_TELEMETRY_TOPIC",
        DEFAULT_TELEMETRY_TOPIC,
    )

    modbus_host = os.getenv(
        "MODBUS_HOST",
        "127.0.0.1",
    )

    modbus_port = int(
        os.getenv(
            "MODBUS_PORT",
            "1502",
        )
    )

    modbus_device_id = int(
        os.getenv(
            "MODBUS_DEVICE_ID",
            "1",
        )
    )

    source_logical_name = (
        modbus_mapping_config[
            "source"
        ]["logical_name"]
    )

    encoding = (
        modbus_mapping_config[
            "encoding"
        ]["float32"]
    )

    # ---------------------------------------------------------
    # Acquisition model
    # ---------------------------------------------------------

    mappings = build_variable_mappings(
        modbus_mapping_config
    )

    windows = build_read_windows(
        mappings
    )

    assert len(mappings) == (
        EXPECTED_VARIABLE_COUNT
    )

    assert len(windows) == 5

    # ---------------------------------------------------------
    # Industrial identity
    # ---------------------------------------------------------

    identity_resolver = (
        PostgresIdentityResolver
        .from_database(
            database_url=database_url,
            source_logical_name=(
                source_logical_name
            ),
        )
    )

    # ---------------------------------------------------------
    # Registry-backed contract
    # ---------------------------------------------------------

    registry_client = (
        ApicurioRegistryClient(
            registry_url,
            timeout=5.0,
        )
    )

    registered_schema = (
        registry_client
        .resolve_avro_schema(
            group_id="ims.telemetry",
            artifact_id=(
                "telemetry-observation"
            ),
            version="1.0.0",
        )
    )

    assert registered_schema.content_id > 0

    codec = TelemetryAvroCodec(
        registered_schema.schema
    )

    framer = ApicurioWireFramer(
        content_id=(
            registered_schema.content_id
        )
    )

    # ---------------------------------------------------------
    # Telemetry transformation
    # ---------------------------------------------------------

    transformer = TelemetryTransformer(
        identity_resolver=(
            identity_resolver
        ),
        source_logical_name=(
            source_logical_name
        ),
    )

    # ---------------------------------------------------------
    # Kafka producer
    # ---------------------------------------------------------

    producer = KafkaTelemetryProducer(
        bootstrap_servers=(
            kafka_bootstrap_servers
        ),
        topic=kafka_topic,
    )

    # ---------------------------------------------------------
    # Kafka consumer
    # ---------------------------------------------------------

    consumer = Consumer(
        {
            "bootstrap.servers": (
                kafka_bootstrap_servers
            ),

            "group.id": (
                "ims-event-pipeline-test-"
                f"{uuid4()}"
            ),

            "enable.auto.commit": False,

            "auto.offset.reset": (
                "latest"
            ),
        }
    )

    try:
        # -----------------------------------------------------
        # Discover Kafka topic
        # -----------------------------------------------------

        metadata = consumer.list_topics(
            topic=kafka_topic,
            timeout=5.0,
        )

        topic_metadata = (
            metadata.topics[
                kafka_topic
            ]
        )

        assert (
            topic_metadata.error
            is None
        )

        assert len(
            topic_metadata.partitions
        ) == 3

        # -----------------------------------------------------
        # Start consumer at current end of each partition
        #
        # This prevents previous test records from being
        # interpreted as part of this pipeline execution.
        # -----------------------------------------------------

        assignment = []

        for partition_id in sorted(
            topic_metadata.partitions
        ):
            topic_partition = (
                TopicPartition(
                    kafka_topic,
                    partition_id,
                )
            )

            (
                _low,
                high,
            ) = (
                consumer
                .get_watermark_offsets(
                    topic_partition,
                    timeout=5.0,
                )
            )

            assignment.append(
                TopicPartition(
                    kafka_topic,
                    partition_id,
                    high,
                )
            )

        consumer.assign(
            assignment
        )

        # -----------------------------------------------------
        # Real Modbus acquisition
        # -----------------------------------------------------

        modbus_client = (
            ModbusAcquisitionClient(
                host=modbus_host,
                port=modbus_port,
                device_id=(
                    modbus_device_id
                ),
                byte_order=encoding[
                    "byte_order"
                ],
                word_order=encoding[
                    "word_order"
                ],
                timeout=3.0,
            )
        )

        try:
            modbus_client.connect()

            readings = acquire_cycle(
                client=modbus_client,
                windows=windows,
            )

        finally:
            modbus_client.close()

        assert len(readings) == (
            EXPECTED_VARIABLE_COUNT
        )

        # -----------------------------------------------------
        # AcquisitionReading -> TelemetryObservation
        # -----------------------------------------------------

        observations = tuple(
            transformer.transform(
                reading
            )
            for reading in readings
        )

        assert len(observations) == (
            EXPECTED_VARIABLE_COUNT
        )

        expected_by_id = {
            observation.telemetry_id:
                observation
            for observation
            in observations
        }

        assert len(expected_by_id) == (
            EXPECTED_VARIABLE_COUNT
        )

        # -----------------------------------------------------
        # Contract -> Avro -> Apicurio -> Kafka
        # -----------------------------------------------------

        for observation in observations:
            avro_payload = (
                codec.serialize(
                    observation
                )
            )

            kafka_value = (
                framer.frame(
                    avro_payload
                )
            )

            producer.publish(
                variable_id=(
                    observation.variable_id
                ),
                value=kafka_value,
            )

        producer.flush(
            timeout=10.0
        )

        # -----------------------------------------------------
        # Consume Kafka records produced by this execution
        # -----------------------------------------------------

        received_by_id = {}

        deadline = (
            time.monotonic()
            + 15.0
        )

        while (
            len(received_by_id)
            < EXPECTED_VARIABLE_COUNT
            and time.monotonic()
            < deadline
        ):
            message = consumer.poll(
                timeout=0.5
            )

            if message is None:
                continue

            if message.error():
                raise AssertionError(
                    "Kafka consumer error: "
                    f"{message.error()}"
                )

            # ---------------------------------------------
            # Apicurio framing
            # ---------------------------------------------

            parsed = (
                ApicurioWireFramer.parse(
                    message.value()
                )
            )

            assert parsed.content_id == (
                registered_schema.content_id
            )

            # ---------------------------------------------
            # Avro -> TelemetryObservation
            # ---------------------------------------------

            restored = (
                codec.deserialize(
                    parsed.payload
                )
            )

            # Ignore unrelated concurrent records,
            # should any exist in the topic.
            if (
                restored.telemetry_id
                not in expected_by_id
            ):
                continue

            # ---------------------------------------------
            # Kafka key must represent variable identity
            # ---------------------------------------------

            expected_key = (
                KafkaTelemetryProducer
                .build_key(
                    restored.variable_id
                )
            )

            assert message.key() == (
                expected_key
            )

            received_by_id[
                restored.telemetry_id
            ] = restored

        # -----------------------------------------------------
        # End-to-end assertions
        # -----------------------------------------------------

        assert len(received_by_id) == (
            EXPECTED_VARIABLE_COUNT
        )

        assert set(
            received_by_id
        ) == set(
            expected_by_id
        )

        for (
            telemetry_id,
            expected_observation,
        ) in expected_by_id.items():
            assert (
                received_by_id[
                    telemetry_id
                ]
                == expected_observation
            )

    finally:
        consumer.close()

        producer.flush(
            timeout=10.0
        )
