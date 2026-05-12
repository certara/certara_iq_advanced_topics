__all__ = ["TransportReaction"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from .base import Reaction


@dataclass(frozen=True)
class TransportReaction(Reaction):
    """A concrete transport reaction using partition coefficient and distribution half-life."""

    partition_coefficient: Expression
    distribution_half_life: Expression

    def deparse(self) -> str:
        return (
            f"{' + '.join(self.reactants)} <-> {' + '.join(self.products)}; "
            f"pdist={deparse_expression(self.partition_coefficient)}, "
            f"tdist={deparse_expression(self.distribution_half_life)}"
        )
