__all__ = ["TemplatedAssignment"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from ..units import Unit


@dataclass(frozen=True, slots=True)
class TemplatedAssignment:
    """A templated assignment whose name and definition may expand."""

    definition: TemplatedExpression
    unit: Unit | None = None
