from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


S7_TYPE_SIZES: Mapping[str, int] = {
    "REAL": 4,
}


@dataclass(frozen=True)
class S7Variable:
    """
    Representa o mapeamento técnico de uma variável na memória S7.
    """

    logical_name: str
    data_type: str
    byte_offset: int

    @property
    def size_bytes(self) -> int:
        try:
            return S7_TYPE_SIZES[self.data_type]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported S7 data type '{self.data_type}'."
            ) from exc

    @property
    def end_offset(self) -> int:
        """
        Retorna o primeiro byte após a região ocupada pela variável.
        """
        return self.byte_offset + self.size_bytes


@dataclass(frozen=True)
class S7DataBlock:
    """
    Representa um Data Block da Reference Plant.
    """

    db_number: int
    logical_name: str
    size_bytes: int
    variables: tuple[S7Variable, ...]

    def get_variable(
        self,
        logical_name: str,
    ) -> S7Variable:
        for variable in self.variables:
            if variable.logical_name == logical_name:
                return variable

        raise KeyError(
            f"Variable '{logical_name}' is not mapped "
            f"in DB{self.db_number}."
        )


@dataclass(frozen=True)
class S7ReferenceModel:
    """
    Representa o modelo completo de memória S7 da Reference Plant.
    """

    name: str
    version: str
    data_blocks: tuple[S7DataBlock, ...]

    def get_data_block(
        self,
        db_number: int,
    ) -> S7DataBlock:
        for data_block in self.data_blocks:
            if data_block.db_number == db_number:
                return data_block

        raise KeyError(
            f"DB{db_number} is not defined."
        )

    def find_variable(
        self,
        logical_name: str,
    ) -> tuple[S7DataBlock, S7Variable]:
        for data_block in self.data_blocks:
            for variable in data_block.variables:
                if variable.logical_name == logical_name:
                    return data_block, variable

        raise KeyError(
            f"Variable '{logical_name}' is not mapped "
            "in the S7 reference model."
        )
