__all__ = ["TemplatedForwardMassActionReaction", "TemplatedReversibleMassActionReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedForwardMassActionReaction(TemplatedReaction):
    """A templated forward mass-action reaction using ``kf``."""

    parameter: TemplatedExpression


@dataclass(frozen=True)
class TemplatedReversibleMassActionReaction(TemplatedReaction):
    """A templated reversible mass-action reaction using ``kf`` and ``kr``."""

    forward_parameter: TemplatedExpression
    reverse_parameter: TemplatedExpression
