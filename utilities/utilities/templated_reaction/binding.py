__all__ = ["TemplatedBindingOnReaction", "TemplatedBindingOffReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedBindingOnReaction(TemplatedReaction):
    """A templated reversible binding reaction parameterized by ``kd`` and ``kon``."""

    dissociation_parameter: TemplatedExpression
    association_rate_parameter: TemplatedExpression


@dataclass(frozen=True)
class TemplatedBindingOffReaction(TemplatedReaction):
    """A templated reversible binding reaction parameterized by ``kd`` and ``koff``."""

    dissociation_parameter: TemplatedExpression
    dissociation_rate_parameter: TemplatedExpression
