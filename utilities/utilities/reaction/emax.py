__all__ = ["EmaxReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.ast import (
    Ascription,
    IntegerLiteral,
)
from ..expressions.deparser import deparse_expression
from ..types import ast as tast
from ..units import ast as uast
from .base import Reaction


@dataclass(frozen=True)
class EmaxReaction(Reaction):
    """A concrete Emax reaction parameterized by ``emax``, ``ec50``, ``n``, and optional ``emin``."""

    maximum_rate: Expression
    half_maximal_effect_concentration: Expression
    hill_coefficient: Expression
    minimum_rate: Expression = Ascription(IntegerLiteral(0), tast.Float64(uast.Dynamic()))

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} -> {' + '.join(self.products)}; "
            f"emax={deparse_expression(self.maximum_rate)}, "
            f"ec50={deparse_expression(self.half_maximal_effect_concentration)}, "
            f"n={deparse_expression(self.hill_coefficient)}, "
            f"emin={deparse_expression(self.minimum_rate)}"
        )
