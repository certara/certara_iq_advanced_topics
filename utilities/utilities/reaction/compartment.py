__all__ = ["Compartment"]

from dataclasses import dataclass
from typing import Literal

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from ..units import Unit
from ..units.deparser import deparse_unit


@dataclass(frozen=True, slots=True)
class Compartment:
    """A concrete compartment declaration with dimension, size, and optional units."""

    dimension: Literal[0, 1, 2, 3]
    size: Expression
    unit: Unit | None = None

    def deparse(self, name: str) -> str:
        if self.unit is not None:
            return f"{name}~{self.dimension}:{deparse_unit(self.unit)} = {deparse_expression(self.size)}"
        else:
            return f"{name}~{self.dimension} = {deparse_expression(self.size)}"
