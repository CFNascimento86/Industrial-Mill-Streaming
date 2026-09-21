from modbus.encoder import encode_modbus_value
from modbus.model import ModbusReferenceModel


class ModbusRuntime:
    """
    Mantém a imagem de memória Modbus da IMS Reference Plant.
    Não implementa comunicação TCP.
    """

    def __init__(
        self,
        model: ModbusReferenceModel,
    ) -> None:
        self._model = model
        self._registers = [0] * self._calculate_register_space()

    def _calculate_register_space(self) -> int:
        if not self._model.registers:
            return 0

        return max(
            register.end_address
            for register in self._model.registers
        )

    @property
    def size(self) -> int:
        return len(self._registers)

    def write_snapshot(
        self,
        snapshot: dict[str, float],
    ) -> None:
        """
        Materializa um Industrial Snapshot no Register Map.
        """

        encoded_values: list[tuple[int, tuple[int, ...]]] = []

        for register in self._model.registers:
            try:
                value = snapshot[register.logical_name]
            except KeyError as exc:
                raise KeyError(
                    "Snapshot missing Modbus-mapped variable: "
                    f"{register.logical_name}"
                ) from exc

            encoded = encode_modbus_value(
                data_type=register.data_type,
                value=value,
                encoding=self._model.encoding,
            )

            if len(encoded) != register.register_count:
                raise ValueError(
                    f"Encoded register count mismatch for "
                    f"'{register.logical_name}'."
                )

            encoded_values.append(
                (register.address, encoded)
            )

        # Commit somente após todo o snapshot ter sido codificado.
        for address, values in encoded_values:
            self._registers[
                address:address + len(values)
            ] = values

    def read_registers(
        self,
        address: int,
        count: int,
    ) -> tuple[int, ...]:
        """
        Retorna uma cópia imutável de uma faixa de Holding Registers.
        """

        if address < 0:
            raise ValueError(
                "Modbus address cannot be negative."
            )

        if count <= 0:
            raise ValueError(
                "Modbus register count must be greater than zero."
            )

        end_address = address + count

        if end_address > len(self._registers):
            raise ValueError(
                "Requested Modbus register range is outside "
                "the runtime address space."
            )

        return tuple(
            self._registers[address:end_address]
        )
