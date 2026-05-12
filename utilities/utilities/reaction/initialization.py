__all__ = ["Initialization", "InitialValue", "SteadyState"]


from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression


class Initialization:
    """Base class for concrete model initialization settings."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class InitialValue(Initialization):
    """Initialize the model from declared state initial values."""

    def deparse(self) -> str:
        return "initial_value()"


@dataclass(frozen=True, slots=True)
class SteadyState(Initialization):
    """Initialize the model by solving to steady state."""

    time_scale: Expression
    max_time: Expression | None = None

    def deparse(self) -> str:
        if self.max_time is None:
            return f"steady_state(time_scale={deparse_expression(self.time_scale)})"
        else:
            return f"steady_state(time_scale={deparse_expression(self.time_scale)}, max_time={deparse_expression(self.max_time)})"
