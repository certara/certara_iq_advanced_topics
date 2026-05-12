__all__ = ["TemplatedEffect", "TemplatedDoseEffect", "TemplatedJumpEffect"]

from abc import abstractmethod
from dataclasses import dataclass

from ordered_set import OrderedSet

from ..templated_expressions import TemplatedExpression, free_variable_names
from ..templated_expressions.ast import BaseTemplatedFunction, TemplatedVariable


class TemplatedEffect:
    """Base class for templated route effects."""

    @abstractmethod
    def get_effect_variables(self) -> OrderedSet:
        pass


@dataclass(frozen=True, slots=True)
class TemplatedDoseEffect(TemplatedEffect):
    """A templated route effect that adds scheduled dose amount to a state."""

    value: TemplatedExpression

    def get_effect_variables(self) -> OrderedSet[TemplatedVariable | BaseTemplatedFunction]:
        return free_variable_names(self.value)


@dataclass(frozen=True, slots=True)
class TemplatedJumpEffect(TemplatedEffect):
    """A templated route effect that sets a state or assignment to a value."""

    value: TemplatedExpression

    def get_effect_variables(self) -> OrderedSet[TemplatedVariable | BaseTemplatedFunction]:
        return free_variable_names(self.value)
