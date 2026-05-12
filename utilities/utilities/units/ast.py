from __future__ import annotations

__all__ = [
    "Unit",
    "Dynamic",
    "ProperUnit",
    "Atom",
    "Dimensionless",
    "Power",
    "Parenthesis",
    "Multiply",
    "Divide",
]

from abc import abstractmethod
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class Unit:
    def __str__(self):
        from .deparser import deparse_unit

        return deparse_unit(self)

    @abstractmethod
    def __mul__(self, other: Unit) -> Unit:
        pass

    @abstractmethod
    def __rmul__(self, other: Unit) -> Unit:
        pass

    @abstractmethod
    def __truediv__(self, other: Unit) -> Unit:
        pass

    @abstractmethod
    def __rtruediv__(self, other: Unit) -> Unit:
        pass


@dataclass(frozen=True, slots=True)
class Dynamic(Unit):
    def __mul__(self, other: Unit) -> Unit:
        if isinstance(other, Unit):
            return self
        return NotImplemented

    def __rmul__(self, other: Unit) -> Unit:
        if isinstance(other, Unit):
            return self
        return NotImplemented

    def __truediv__(self, other: Unit) -> Unit:
        if isinstance(other, Unit):
            return self
        return NotImplemented

    def __rtruediv__(self, other: Unit) -> Unit:
        if isinstance(other, Unit):
            return self
        return NotImplemented


@dataclass(frozen=True, slots=True)
class ProperUnit(Unit):
    def __mul__(self, other: ProperUnit) -> ProperUnit:
        if isinstance(other, ProperUnit):
            return Multiply(self, other)
        return NotImplemented

    def __rmul__(self, other: ProperUnit) -> ProperUnit:
        if isinstance(other, ProperUnit):
            return Multiply(other, self)
        return NotImplemented

    def __truediv__(self, other: ProperUnit) -> ProperUnit:
        if isinstance(other, ProperUnit):
            return Divide(self, other)
        return NotImplemented

    def __rtruediv__(self, other: ProperUnit) -> ProperUnit:
        if isinstance(other, ProperUnit):
            return Divide(other, self)
        return NotImplemented

    def __eq__(self, other: ProperUnit) -> bool:
        from .comparison import is_equivalent

        if isinstance(other, ProperUnit):
            return is_equivalent(self, other)
        return NotImplemented


# eq=False prevents overriding the ProperUnit.__eq__ method
@dataclass(frozen=True, slots=True, eq=False)
class Atom(ProperUnit):
    symbol: str


@dataclass(frozen=True, slots=True, eq=False)
class Dimensionless(ProperUnit):
    pass


@dataclass(frozen=True, slots=True, eq=False)
class Power(ProperUnit):
    base: ProperUnit
    exponent: int | Fraction


@dataclass(frozen=True, slots=True, eq=False)
class Parenthesis(ProperUnit):
    contents: ProperUnit


@dataclass(frozen=True, slots=True, eq=False)
class Multiply(ProperUnit):
    left: ProperUnit
    right: ProperUnit


@dataclass(frozen=True, slots=True, eq=False)
class Divide(ProperUnit):
    left: ProperUnit
    right: ProperUnit
