__all__ = ["TemplatedSteadyStateReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedSteadyStateReaction(TemplatedReaction):
    """A templated reversible reaction driven by steady-state concentration and half-life."""

    steady_state_concentration: TemplatedExpression
    half_life: TemplatedExpression
    volume: TemplatedExpression | None = None
