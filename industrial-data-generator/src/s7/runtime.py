from __future__ import annotations
from typing import Mapping
from .encoder import encode_s7_value
from .model import S7ReferenceModel


class S7Runtime:
    """
    Materializa snapshots industriais na imagem de memória S7
    da Reference Plant.
    O runtime não implementa comunicação de rede.
    """

    def __init__(
        self,
        *,
        model: S7ReferenceModel,
    ) -> None:
        self._model = model

        self._memory = {
            data_block.db_number: bytearray(
                data_block.size_bytes
            )
            for data_block
            in model.data_blocks
        }

    @property
    def model(
        self,
    ) -> S7ReferenceModel:
        return self._model

    def write_snapshot(
        self,
        snapshot: Mapping[str, float],
    ) -> None:
        """
        Escreve um snapshot industrial completo na memória S7.
        """

        for data_block in self._model.data_blocks:
            memory = self._memory[
                data_block.db_number
            ]

            for variable in data_block.variables:
                try:
                    value = snapshot[
                        variable.logical_name
                    ]
                except KeyError as exc:
                    raise KeyError(
                        f"Snapshot does not contain "
                        f"'{variable.logical_name}'."
                    ) from exc

                encoded = encode_s7_value(
                    data_type=variable.data_type,
                    value=value,
                )

                start = (
                    variable.byte_offset
                )

                end = (
                    start
                    + variable.size_bytes
                )

                memory[
                    start:end
                ] = encoded

    def read_db(
        self,
        db_number: int,
    ) -> bytes:
        """
        Retorna uma cópia imutável da imagem de um DB.
        """

        try:
            memory = self._memory[
                db_number
            ]
        except KeyError as exc:
            raise KeyError(
                f"DB{db_number} is not available in the runtime."
            ) from exc

        return bytes(
            memory
        )

    def read_area(
        self,
        *,
        db_number: int,
        byte_offset: int,
        size_bytes: int,
    ) -> bytes:
        """
        Retorna uma região específica de um DB.
        """

        if byte_offset < 0:
            raise ValueError(
                "byte_offset cannot be negative."
            )

        if size_bytes <= 0:
            raise ValueError(
                "size_bytes must be greater than zero."
            )

        data = self.read_db(
            db_number
        )

        end = (
            byte_offset
            + size_bytes
        )

        if end > len(data):
            raise ValueError(
                f"Requested area exceeds DB{db_number} size."
            )

        return data[
            byte_offset:end
        ]
      
