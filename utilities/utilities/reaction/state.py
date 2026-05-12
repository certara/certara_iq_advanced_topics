__all__ = ["State"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from ..units import Unit
from ..units.deparser import deparse_unit


@dataclass(frozen=True, slots=True)
class State:
    """A concrete state declaration with optional compartment and units."""

    initial_value: Expression
    compartment: str | None = None
    unit: Unit | None = None

    def deparse(self, name: str) -> str:
        if self.compartment is not None:
            if self.unit is not None:
                return (
                    f"{name}@{self.compartment}:{deparse_unit(self.unit)} *= {deparse_expression(self.initial_value)}"
                )
            else:
                return f"{name}@{self.compartment} *= {deparse_expression(self.initial_value)}"
        else:
            if self.unit is not None:
                return f"{name}:{deparse_unit(self.unit)} *= {deparse_expression(self.initial_value)}"
            else:
                return f"{name} *= {deparse_expression(self.initial_value)}"
