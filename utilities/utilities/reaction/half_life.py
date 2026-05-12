__all__ = ["HalfLifeReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from .base import Reaction


@dataclass(frozen=True)
class HalfLifeReaction(Reaction):
    """A concrete first-order loss or conversion reaction using ``thalf``."""

    half_life: Expression

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} -> {' + '.join(self.products)}; thalf={deparse_expression(self.half_life)}"
        )
