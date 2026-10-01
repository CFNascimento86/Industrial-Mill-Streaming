from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


MODBUS_REGISTER_COUNTS = {
    "FLOAT32": 2,
}


@dataclass(frozen=True)
class VariableMapping:
    logical_name: str
    address: int
    data_type: str

    @property
    def register_count(self) -> int:
        try:
            return MODBUS_REGISTER_COUNTS[
                self.data_type
            ]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported data type: {self.data_type}"
            ) from exc

    @property
    def end_address(self) -> int:
        return (
            self.address
            + self.register_count
        )


@dataclass(frozen=True)
class ReadWindow:
    address: int
    count: int
    variables: tuple[
        VariableMapping,
        ...
    ]


@dataclass(frozen=True)
class AcquisitionReading:
    logical_name: str
    value: float
    observed_at: datetime
    quality: str
