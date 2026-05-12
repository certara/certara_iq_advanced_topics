from __future__ import annotations

__all__ = ["TemplatedTransportReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedTransportReaction(TemplatedReaction):
    """A templated transport reaction using partition coefficient and distribution half-life."""

    partition_coefficient: TemplatedExpression
    distribution_half_life: TemplatedExpression
