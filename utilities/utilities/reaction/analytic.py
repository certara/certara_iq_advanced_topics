__all__ = ["ForwardAnalyticReaction", "ReversibleAnalyticReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from .base import Reaction


@dataclass(frozen=True)
class ForwardAnalyticReaction(Reaction):
    """A concrete forward reaction with an explicit rate expression."""

    rate: Expression

    def deparse(self) -> str:
        return f"{' + '.join(self.reactants)} -> {' + '.join(self.products)}; rf={deparse_expression(self.rate)}"


@dataclass(frozen=True)
class ReversibleAnalyticReaction(Reaction):
    """A concrete reversible reaction with explicit forward and reverse rates."""

    forward_rate: Expression
    reverse_rate: Expression

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} <-> {' + '.join(self.products)}; "
            f"rf={deparse_expression(self.forward_rate)}, rr={deparse_expression(self.reverse_rate)}"
        )
