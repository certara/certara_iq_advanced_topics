from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from ..units import Unit


@dataclass(frozen=True, slots=True)
class TemplatedParameter:
    """A templated parameter declaration, optionally with units."""

    value: TemplatedExpression
    unit: Unit | None = None
