__all__ = ["Effect", "DoseEffect", "JumpEffect"]

from abc import abstractmethod
from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression


class Effect:
    """Base class for concrete route effects."""

    @abstractmethod
    def deparse(self, name: str) -> str:
        pass


@dataclass(frozen=True, slots=True)
class DoseEffect(Effect):
    """A route effect that adds scheduled dose amount to a state."""

    value: Expression

    def deparse(self, name: str) -> str:
        return f"{name} += amt * {deparse_expression(self.value)}"


@dataclass(frozen=True, slots=True)
class JumpEffect(Effect):
    """A route effect that sets a state or assignment to a value."""

    value: Expression

    def deparse(self, name: str) -> str:
        return f"{name} = {deparse_expression(self.value)}"
