from __future__ import annotations
import struct
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException


MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 1502
MODBUS_DEVICE_ID = 1

CANE_FLOW_ADDRESS = 14
CANE_FLOW_REGISTER_COUNT = 2


def decode_float32_big_endian(
    registers: list[int],
) -> float:
    """
    Decodifica dois Holding Registers em FLOAT32.
    Convenção IMS:
        byte_order = big_endian
        word_order = big_endian
    """

    if len(registers) != 2:
        raise ValueError(
            "FLOAT32 requires exactly two registers."
        )

    raw_bytes = struct.pack(
        ">HH",
        registers[0],
        registers[1],
    )

    return struct.unpack(
        ">f",
        raw_bytes,
    )[0]


def main() -> None:
    client = ModbusTcpClient(
        host=MODBUS_HOST,
        port=MODBUS_PORT,
        timeout=3,
    )

    try:
        print(
            f"Connecting to "
            f"{MODBUS_HOST}:{MODBUS_PORT}..."
        )

        if not client.connect():
            raise ConnectionError(
                "Could not connect to "
                "IMS Reference Plant."
            )

        response = client.read_holding_registers(
            CANE_FLOW_ADDRESS,
            count=CANE_FLOW_REGISTER_COUNT,
            device_id=MODBUS_DEVICE_ID,
        )

        if response.isError():
            raise RuntimeError(
                f"Modbus error response: {response}"
            )

        registers = response.registers

        cane_flow = decode_float32_big_endian(
            registers
        )

        print(
            f"HR[{CANE_FLOW_ADDRESS}]     = "
            f"{registers[0]}"
        )

        print(
            f"HR[{CANE_FLOW_ADDRESS + 1}] = "
            f"{registers[1]}"
        )

        print(
            f"cane_flow = {cane_flow:.2f}"
        )

    except ModbusException as exc:
        raise RuntimeError(
            f"Modbus communication failed: {exc}"
        ) from exc

    finally:
        client.close()


if __name__ == "__main__":
    main()
