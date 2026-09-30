from __future__ import annotations
import logging
from modbus.runtime import ModbusRuntime
from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import (
    DataType,
    SimData,
    SimDevice,
)


LOGGER = logging.getLogger(
    "ims.modbus_server"
)


class PyModbusServerAdapter:
    """
    Materializa o ModbusRuntime através de uma interface Modbus TCP.
    O ModbusRuntime permanece como representação canônica dos
    Holding Registers. O PyModbus é utilizado exclusivamente
    como mecanismo de comunicação.
    """

    HOLDING_REGISTER_FUNCTION_CODE = 3

    def __init__(
        self,
        *,
        runtime: ModbusRuntime,
        host: str,
        port: int,
        device_id: int,
    ) -> None:
        if not host:
            raise ValueError(
                "Modbus host cannot be empty."
            )

        if not 1 <= port <= 65535:
            raise ValueError(
                "Modbus port must be between 1 and 65535."
            )

        if not 1 <= device_id <= 247:
            raise ValueError(
                "Modbus device ID must be between 1 and 247."
            )

        if runtime.size <= 0:
            raise ValueError(
                "ModbusRuntime must contain at least one register."
            )

        self._runtime = runtime
        self._host = host
        self._port = port
        self._device_id = device_id
        self._started = False

        # O datastore do PyModbus é apenas a materialização
        # da imagem de registradores mantida pelo ModbusRuntime.
        register_block = SimData(
            address=0,
            values=[0] * runtime.size,
            datatype=DataType.REGISTERS,
        )

        self._device = SimDevice(
            id=device_id,
            simdata=register_block,
        )

        self._server = ModbusTcpServer(
            context=self._device,
            address=(
                host,
                port,
            ),
            ignore_missing_devices=False,
        )

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def device_id(self) -> int:
        return self._device_id

    async def start(self) -> None:
        """
        Inicia o servidor Modbus TCP em background.
        """

        if self._started:
            return

        await self._server.serve_forever(
            background=True
        )

        self._started = True

        LOGGER.info(
            "Modbus TCP Server started at %s:%d "
            "| device_id=%d",
            self._host,
            self._port,
            self._device_id,
        )

    async def sync_from_runtime(self) -> None:
        """
        Sincroniza a imagem canônica do ModbusRuntime
        com o datastore exposto pelo servidor.
        """

        if not self._started:
            raise RuntimeError(
                "Modbus TCP Server is not running."
            )

        values = list(
            self._runtime.read_registers(
                address=0,
                count=self._runtime.size,
            )
        )

        await self._server.async_setValues(
            self._device_id,
            self.HOLDING_REGISTER_FUNCTION_CODE,
            0,
            values,
        )

    async def stop(self) -> None:
        """
        Encerra o servidor Modbus TCP.
        """

        if not self._started:
            return

        await self._server.shutdown()

        self._started = False

        LOGGER.info(
            "Modbus TCP Server stopped."
        )
