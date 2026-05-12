__all__ = ["SteadyStateReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from .base import Reaction


@dataclass(frozen=True)
class SteadyStateReaction(Reaction):
    """A concrete reversible reaction driven by steady-state concentration and half-life."""

    steady_state_concentration: Expression
    half_life: Expression
    volume: Expression | None = None

    def deparse(self) -> str:
        if self.volume is None:
            return (
                f"{' + '.join(self.reactants)} <-> {' + '.join(self.products)}; "
                f"css={deparse_expression(self.steady_state_concentration)}, "
                f"thalf={deparse_expression(self.half_life)}"
            )
        else:
            return (
                f"{' + '.join(self.reactants)} <-> {' + '.join(self.products)}; "
                f"css={deparse_expression(self.steady_state_concentration)}, "
                f"thalf={deparse_expression(self.half_life)}, "
                f"v={deparse_expression(self.volume)}"
            )
