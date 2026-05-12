__all__ = ["TemplatedMichaelisMentenReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedMichaelisMentenReaction(TemplatedReaction):
    """A templated Michaelis-Menten reaction using ``km``, ``kcat``, and enzyme amount."""

    michaelis_parameter: TemplatedExpression
    catalytic_rate_parameter: TemplatedExpression
    enzyme_amount: TemplatedExpression
