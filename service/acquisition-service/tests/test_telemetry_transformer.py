from __future__ import annotations
from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

import pytest

from acquisition_service.contract import (
    ObservedAtSource,
    TelemetryQuality,
)
from acquisition_service.identity import (
    ResolvedIdentity,
)
from acquisition_service.model import (
    AcquisitionReading,
)
from acquisition_service.transformer import (
    TelemetryTransformationError,
    TelemetryTransformer,
)


VARIABLE_ID = UUID(
    "11111111-1111-4111-8111-111111111111"
)

SOURCE_ID = UUID(
    "22222222-2222-4222-8222-222222222222"
)

TELEMETRY_ID = UUID(
    "33333333-3333-4333-8333-333333333333"
)


class FakeIdentityResolver:
    def resolve(
        self,
        *,
        variable_logical_name: str,
        source_logical_name: str,
    ) -> ResolvedIdentity:
        return ResolvedIdentity(
            variable_id=VARIABLE_ID,
            variable_logical_name=(
                variable_logical_name
            ),
            source_id=SOURCE_ID,
            source_logical_name=(
                source_logical_name
            ),
        )


def test_acquisition_reading_becomes_telemetry_observation():
    observed_at = datetime(
        2026,
        10,
        6,
        18,
        30,
        1,
        tzinfo=timezone.utc,
    )

    ingested_at = datetime(
        2026,
        10,
        6,
        18,
        30,
        2,
        tzinfo=timezone.utc,
    )

    transformer = TelemetryTransformer(
        identity_resolver=(
            FakeIdentityResolver()
        ),
        source_logical_name=(
            "s7_1500_milling"
        ),
        id_factory=lambda: TELEMETRY_ID,
        clock=lambda: ingested_at,
    )

    reading = AcquisitionReading(
        logical_name="cane_flow",
        value=301.42,
        observed_at=observed_at,
        quality="UNKNOWN",
    )

    observation = transformer.transform(
        reading
    )

    assert observation.telemetry_id == (
        TELEMETRY_ID
    )

    assert observation.variable_id == (
        VARIABLE_ID
    )

    assert (
        observation.variable_logical_name
        == "cane_flow"
    )

    assert observation.source_id == (
        SOURCE_ID
    )

    assert (
        observation.source_logical_name
        == "s7_1500_milling"
    )

    assert observation.value == pytest.approx(
        301.42
    )

    assert observation.quality == (
        TelemetryQuality.UNKNOWN
    )

    assert observation.observed_at == (
        observed_at
    )

    assert observation.observed_at_source == (
        ObservedAtSource.ACQUISITION
    )

    assert observation.ingested_at == (
        ingested_at
    )


def test_transformer_rejects_non_finite_value():
    transformer = TelemetryTransformer(
        identity_resolver=(
            FakeIdentityResolver()
        ),
        source_logical_name=(
            "s7_1500_milling"
        ),
    )

    reading = AcquisitionReading(
        logical_name="cane_flow",
        value=float("nan"),
        observed_at=datetime.now(
            timezone.utc
        ),
        quality="UNKNOWN",
    )

    with pytest.raises(
        TelemetryTransformationError,
        match="must be finite",
    ):
        transformer.transform(
            reading
        )


def test_transformer_rejects_naive_observed_at():
    transformer = TelemetryTransformer(
        identity_resolver=(
            FakeIdentityResolver()
        ),
        source_logical_name=(
            "s7_1500_milling"
        ),
    )

    reading = AcquisitionReading(
        logical_name="cane_flow",
        value=300.0,
        observed_at=datetime(
            2026,
            10,
            6,
            18,
            30,
        ),
        quality="UNKNOWN",
    )

    with pytest.raises(
        TelemetryTransformationError,
        match="timezone-aware",
    ):
        transformer.transform(
            reading
        )


def test_transformer_rejects_unknown_quality():
    transformer = TelemetryTransformer(
        identity_resolver=(
            FakeIdentityResolver()
        ),
        source_logical_name=(
            "s7_1500_milling"
        ),
    )

    reading = AcquisitionReading(
        logical_name="cane_flow",
        value=300.0,
        observed_at=datetime.now(
            timezone.utc
        ),
        quality="EXCELLENT",
    )

    with pytest.raises(
        TelemetryTransformationError,
        match="Unsupported telemetry quality",
    ):
        transformer.transform(
            reading
        )
