__all__ = ["BindingOnReaction", "BindingOffReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from .base import Reaction


@dataclass(frozen=True)
class BindingOnReaction(Reaction):
    """A concrete reversible binding reaction parameterized by ``kd`` and ``kon``."""

    dissociation_parameter: Expression
    association_rate_parameter: Expression

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} <-> {' + '.join(self.products)}; "
            f"kd={deparse_expression(self.dissociation_parameter)}, kon={deparse_expression(self.association_rate_parameter)}"
        )


@dataclass(frozen=True)
class BindingOffReaction(Reaction):
    """A concrete reversible binding reaction parameterized by ``kd`` and ``koff``."""

    dissociation_parameter: Expression
    dissociation_rate_parameter: Expression

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} <-> {' + '.join(self.products)}; "
            f"kd={deparse_expression(self.dissociation_parameter)}, koff={deparse_expression(self.dissociation_rate_parameter)}"
        )
