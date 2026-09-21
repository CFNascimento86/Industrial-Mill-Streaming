from dataclasses import dataclass


MODBUS_TYPE_REGISTER_COUNTS = {
    "FLOAT32": 2,
}


@dataclass(frozen=True)
class ModbusRegister:
    """
    Representa o mapeamento técnico de uma variável no espaço Modbus.
    """

    logical_name: str
    address: int
    data_type: str

    @property
    def register_count(self) -> int:
        try:
            return MODBUS_TYPE_REGISTER_COUNTS[self.data_type]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported Modbus data type: {self.data_type}"
            ) from exc

    @property
    def end_address(self) -> int:
        """
        Endereço exclusivo do intervalo ocupado.
        Exemplo:
            address = 14
            register_count = 2
            ocupa HR[14] e HR[15]
            end_address = 16
        """
        return self.address + self.register_count


@dataclass(frozen=True)
class ModbusEncoding:
    byte_order: str
    word_order: str


@dataclass(frozen=True)
class ModbusReferenceModel:
    name: str
    version: str
    process: str
    addressing: str
    register_type: str
    encoding: ModbusEncoding
    registers: tuple[ModbusRegister, ...]

    def get_register(self, logical_name: str) -> ModbusRegister:
        for register in self.registers:
            if register.logical_name == logical_name:
                return register

        raise KeyError(
            f"Variable not mapped in Modbus model: {logical_name}"
        )
