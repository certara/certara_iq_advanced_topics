__all__ = ["MichaelisMentenReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from .base import Reaction


@dataclass(frozen=True)
class MichaelisMentenReaction(Reaction):
    """A concrete Michaelis-Menten reaction using ``km``, ``kcat``, and enzyme amount."""

    michaelis_parameter: Expression
    catalytic_rate_parameter: Expression
    enzyme_amount: Expression

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} -> {' + '.join(self.products)}; "
            f"km={deparse_expression(self.michaelis_parameter)}, "
            f"kcat={deparse_expression(self.catalytic_rate_parameter)}, "
            f"e={deparse_expression(self.enzyme_amount)}"
        )
