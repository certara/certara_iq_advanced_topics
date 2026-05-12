__all__ = ["TemplatedCompartment"]

from dataclasses import dataclass
from typing import Literal

from ..templated_expressions import TemplatedExpression
from ..units import Unit


@dataclass(frozen=True, slots=True)
class TemplatedCompartment:
    """A templated compartment declaration with dimension, size, and optional units."""

    dimension: Literal[0, 1, 2, 3]
    size: TemplatedExpression
    unit: Unit | None = None
