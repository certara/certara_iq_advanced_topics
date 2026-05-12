__all__ = ["Assignment"]
from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from ..units import Unit
from ..units.deparser import deparse_unit


@dataclass(frozen=True, slots=True)
class Assignment:
    """A concrete ReactionModel assignment derived from an expression."""

    definition: Expression
    unit: Unit | None = None

    def deparse(self, name: str) -> str:
        if self.unit is not None:
            return f"{name}:{deparse_unit(self.unit)} = {deparse_expression(self.definition)}"
        else:
            return f"{name} = {deparse_expression(self.definition)}"
