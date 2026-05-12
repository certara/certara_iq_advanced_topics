from __future__ import annotations

__all__ = ["TemplatedEmaxReaction"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression
from ..templated_expressions.ast import (
    Ascription,
    IntegerLiteral,
)
from ..types import ast as tast
from ..units import ast as uast
from .base import TemplatedReaction


@dataclass(frozen=True)
class TemplatedEmaxReaction(TemplatedReaction):
    """A templated Emax reaction parameterized by ``emax``, ``ec50``, ``n``, and optional ``emin``."""

    maximum_rate: TemplatedExpression
    half_maximal_effect_concentration: TemplatedExpression
    hill_coefficient: TemplatedExpression
    minimum_rate: TemplatedExpression = Ascription(IntegerLiteral(0), tast.Float64(uast.Dynamic()))
