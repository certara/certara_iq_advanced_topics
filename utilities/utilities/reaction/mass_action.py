__all__ = ["ForwardMassActionReaction", "ReversibleMassActionReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from .base import Reaction


@dataclass(frozen=True)
class ForwardMassActionReaction(Reaction):
    """A concrete forward mass-action reaction using ``kf``."""

    parameter: Expression

    def deparse(self) -> str:
        return f"{' + '.join(self.reactants)} -> {' + '.join(self.products)}; kf={deparse_expression(self.parameter)}"


@dataclass(frozen=True)
class ReversibleMassActionReaction(Reaction):
    """A concrete reversible mass-action reaction using ``kf`` and ``kr``."""

    forward_parameter: Expression
    reverse_parameter: Expression

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} <-> {' + '.join(self.products)}; "
            f"kf={deparse_expression(self.forward_parameter)}, kr={deparse_expression(self.reverse_parameter)}"
        )
