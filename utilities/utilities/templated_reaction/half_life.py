__all__ = ["TemplatedHalfLifeReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedHalfLifeReaction(TemplatedReaction):
    """A templated first-order loss or conversion reaction using ``thalf``."""

    half_life: TemplatedExpression
