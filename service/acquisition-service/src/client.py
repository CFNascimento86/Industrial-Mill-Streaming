from __future__ import annotations
from datetime import (
    datetime,
    timezone,
)

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from acquisition_service.decoder import decode_value
from acquisition_service.model import (
    AcquisitionReading,
    ReadWindow,
)


class AcquisitionError(RuntimeError):
    """
    Falha operacional durante aquisição da fonte industrial.
    """


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
        self._host = host
        self._port = port
        self._device_id = device_id

        self._byte_order = byte_order
        self._word_order = word_order

        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=timeout,

            # A política de retry/reconnect pertence ao IMS,
            # não ao cliente da biblioteca.
            retries=0,
        )

    @property
    def connected(self) -> bool:
        return bool(
            self._client.connected
        )

    def connect(self) -> None:
        """
        Estabelece conexão com a fonte Modbus.
        """

        try:
            connected = self._client.connect()

        except (
            ModbusException,
            OSError,
            TimeoutError,
        ) as exc:
            raise AcquisitionError(
                "Could not connect to Modbus source "
                f"{self._host}:{self._port}."
            ) from exc

        if not connected:
            raise AcquisitionError(
                "Could not connect to Modbus source "
                f"{self._host}:{self._port}."
            )

    def close(self) -> None:
        """
        Encerra a conexão Modbus.
        """

        self._client.close()

    def read_window(
        self,
        window: ReadWindow,
    ) -> tuple[
        AcquisitionReading,
        ...
    ]:
        """
        Executa uma leitura FC03 e converte os registradores
        em observações industriais.
        """

        try:
            response = (
                self._client
                .read_holding_registers(
                    window.address,
                    count=window.count,
                    device_id=self._device_id,
                )
            )

        except (
            ModbusException,
            OSError,
            TimeoutError,
        ) as exc:
            raise AcquisitionError(
                "Modbus communication failure "
                f"while reading address "
                f"{window.address} "
                f"count {window.count}."
            ) from exc

        if response is None:
            raise AcquisitionError(
                "Modbus source returned no response "
                f"for address {window.address}."
            )

        if response.isError():
            raise AcquisitionError(
                "Modbus source returned an error "
                f"response for address "
                f"{window.address}: {response}"
            )

        registers = response.registers

        if len(registers) != window.count:
            raise AcquisitionError(
                "Incomplete Modbus response: "
                f"expected {window.count} registers, "
                f"received {len(registers)}."
            )

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
