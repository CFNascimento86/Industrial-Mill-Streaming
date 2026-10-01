from __future__ import annotations
from datetime import (
    datetime,
    timezone,
)

from pymodbus.client import (
    ModbusTcpClient,
)
from pymodbus.exceptions import (
    ModbusException,
)

from acquisition_service.decoder import (
    decode_value,
)
from acquisition_service.model import (
    AcquisitionReading,
    ReadWindow,
)


class AcquisitionError(RuntimeError):
    pass


class ModbusAcquisitionClient:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        device_id: int,
        byte_order: str,
        word_order: str,
        timeout: float = 3.0,
    ) -> None:
        self._device_id = device_id

        self._byte_order = byte_order
        self._word_order = word_order

        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=timeout,
        )

    def connect(self) -> None:
        if not self._client.connect():
            raise AcquisitionError(
                "Could not connect to Modbus source."
            )

    def close(self) -> None:
        self._client.close()

    def read_window(
        self,
        window: ReadWindow,
    ) -> tuple[
        AcquisitionReading,
        ...
    ]:
        try:
            response = (
                self._client
                .read_holding_registers(
                    window.address,
                    count=window.count,
                    device_id=self._device_id,
                )
            )

        except ModbusException as exc:
            raise AcquisitionError(
                "Modbus communication failure."
            ) from exc

        if response.isError():
            raise AcquisitionError(
                "Modbus source returned an "
                f"error response: {response}"
            )

        registers = response.registers

        observed_at = datetime.now(
            timezone.utc
        )

        readings: list[
            AcquisitionReading
        ] = []

        for variable in window.variables:
            relative_address = (
                variable.address
                - window.address
            )

            variable_registers = registers[
                relative_address:
                relative_address
                + variable.register_count
            ]

            value = decode_value(
                data_type=variable.data_type,
                registers=variable_registers,
                byte_order=self._byte_order,
                word_order=self._word_order,
            )

            readings.append(
                AcquisitionReading(
                    logical_name=(
                        variable.logical_name
                    ),
                    value=value,
                    observed_at=observed_at,
                    quality="UNKNOWN",
                )
            )

        return tuple(readings)
