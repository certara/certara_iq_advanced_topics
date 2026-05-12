__all__ = ["TemplatedState"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from ..units import Unit


@dataclass(frozen=True, slots=True)
class TemplatedState:
    """A templated state declaration with optional compartment and units."""

    initial_value: TemplatedExpression
    compartment: str | None = None
    unit: Unit | None = None
