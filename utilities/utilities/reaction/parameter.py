__all__ = ["Parameter"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from ..units import Unit
from ..units.deparser import deparse_unit


@dataclass(frozen=True, slots=True)
class Parameter:
    """A concrete ReactionModel parameter declaration, optionally with units."""

    value: Expression
    unit: Unit | None = None

    def deparse(self, name: str) -> str:
        if self.unit is not None:
            return f"{name}:{deparse_unit(self.unit)} := {deparse_expression(self.value)}"
        else:
            return f"{name} := {deparse_expression(self.value)}"
