__all__ = ["TemplatedForwardAnalyticReaction", "TemplatedReversibleAnalyticReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedForwardAnalyticReaction(TemplatedReaction):
    """A templated forward reaction with an explicit rate expression."""

    rate: TemplatedExpression


@dataclass(frozen=True)
class TemplatedReversibleAnalyticReaction(TemplatedReaction):
    """A templated reversible reaction with explicit forward and reverse rates."""

    forward_rate: TemplatedExpression
    reverse_rate: TemplatedExpression
