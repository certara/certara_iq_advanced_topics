from __future__ import annotations

__all__ = [
    "InferrableType",
    "DeclarableType",
    "Dynamic",
    "ProperType",
    "Nothing",
    "ValueType",
    "Array",
    "DataType",
    "Boolean",
    "Integer64",
    "Float64",
    "String",
    "NumericLiteral",
    "IntegerLiteral",
    "FractionalLiteral",
    "FloatLiteral",
]

from abc import abstractmethod
from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from ..units.ast import Dimensionless, Unit
from .utility import float_divide, float_equals, float_power


@dataclass(frozen=True, slots=True)
class InferrableType:
    pass


@dataclass(frozen=True, slots=True)
class DeclarableType(InferrableType):
    def __str__(self):
        from .deparser import deparse_type

        return deparse_type(self)


@dataclass(frozen=True, slots=True)
class Dynamic(DeclarableType):
    def __mul__(self, other: InferrableType) -> InferrableType:
        if isinstance(other, InferrableType):
            return self
        return NotImplemented

    def __rmul__(self, other: InferrableType) -> InferrableType:
        if isinstance(other, InferrableType):
            return self
        return NotImplemented

    def __truediv__(self, other: InferrableType) -> InferrableType:
        if isinstance(other, InferrableType):
            return self
        return NotImplemented

    def __rtruediv__(self, other: InferrableType) -> InferrableType:
        if isinstance(other, InferrableType):
            return self
        return NotImplemented

    def __pow__(self, other: InferrableType) -> InferrableType:
        if isinstance(other, InferrableType):
            return self
        return NotImplemented

    def __rpow__(self, other: InferrableType) -> InferrableType:
        if isinstance(other, InferrableType):
            return self
        return NotImplemented


@dataclass(frozen=True, slots=True)
class ProperType(DeclarableType):
    pass


@dataclass(frozen=True, slots=True)
class Nothing(ProperType):
    def to_numpy(self):
        return np.dtype(float)

    def __mul__(self, other: ProperType | NumericLiteral) -> InferrableType:
        match other:
            case ProperType() | NumericLiteral():
                return self
            case _:
                return NotImplemented

    def __rmul__(self, other: ProperType | NumericLiteral) -> InferrableType:
        match other:
            case ProperType() | NumericLiteral():
                return self
            case _:
                return NotImplemented

    def __truediv__(self, other: ProperType | NumericLiteral) -> InferrableType:
        match other:
            case ProperType() | NumericLiteral():
                return self
            case _:
                return NotImplemented

    def __rtruediv__(self, other: ProperType | NumericLiteral) -> InferrableType:
        match other:
            case ProperType() | NumericLiteral():
                return self
            case _:
                return NotImplemented

    def __pow__(self, other: ProperType | NumericLiteral) -> InferrableType:
        match other:
            case ProperType() | NumericLiteral():
                return self
            case _:
                return NotImplemented

    def __rpow__(self, other: ProperType | NumericLiteral) -> InferrableType:
        match other:
            case ProperType() | NumericLiteral():
                return self
            case _:
                return NotImplemented


@dataclass(frozen=True, slots=True)
class ValueType(ProperType):
    pass


@dataclass(frozen=True, slots=True)
class Array(ValueType):
    element_type: DataType | Dynamic | Nothing


@dataclass(frozen=True, slots=True)
class DataType(ValueType):
    @staticmethod
    def from_numpy(dtype: np.dtype) -> DataType:
        match dtype.kind:
            case "b":
                return Boolean()
            case "i":
                return Integer64()
            case "f":
                return Float64()
            case "U":
                return String()
            case _:
                raise NotImplementedError(f"Unsupported dtype: {dtype}")

    def to_numpy(self):
        raise NotImplementedError()

    @abstractmethod
    def cast(self, value: object) -> str | bool | int | float:
        raise NotImplementedError()


@dataclass(frozen=True, slots=True)
class Boolean(DataType):
    def to_numpy(self):
        return np.dtype(bool)

    def cast(self, value: object) -> bool:
        match value:
            case bool():
                return value
            case _:
                raise TypeError(f"Expected boolean, got {type(value)}: {value}")


@dataclass(frozen=True, slots=True)
class Integer64(DataType):
    def to_numpy(self):
        return np.dtype(int)

    def cast(self, value: object) -> int:
        match value:
            case int():
                return value
            case _:
                raise TypeError(f"Expected integer, got {type(value)}: {value}")

    def __add__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Integer64()
            case _:
                return NotImplemented

    def __sub__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Integer64()
            case _:
                return NotImplemented

    def __mul__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Integer64()
            case _:
                return NotImplemented

    def __pow__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __truediv__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Float64()
            case _:
                return NotImplemented


@dataclass(frozen=True, slots=True)
class Float64(DataType):
    unit: Unit = Dimensionless()

    def to_numpy(self):
        return np.dtype(float)

    def cast(self, value: object) -> float:
        match value:
            case int() | float():
                return float(value)
            case _:
                raise TypeError(f"Expected number, got {type(value)}: {value}")

    def __mul__(self, other: Integer64 | Float64) -> InferrableType:
        match other:
            case Integer64():
                return self
            case Float64(right_unit):
                return Float64(self.unit * right_unit)
            case _:
                return NotImplemented

    def __rmul__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return self
            case _:
                return NotImplemented

    def __truediv__(self, other: Integer64 | Float64) -> InferrableType:
        match other:
            case Integer64():
                return Float64()
            case Float64(right_unit):
                return Float64(self.unit / right_unit)
            case _:
                return NotImplemented

    def __rtruediv__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Float64(Dimensionless() / self.unit)
            case _:
                return NotImplemented


@dataclass(frozen=True, slots=True)
class String(DataType):
    def to_numpy(self):
        return np.dtype(str)

    def cast(self, value: object) -> str:
        match value:
            case str():
                return value
            case _:
                raise TypeError(f"Expected string, got {type(value)}: {value}")


@dataclass(frozen=True, slots=True)
class NumericLiteral(InferrableType):
    # Math between literals that could result in an integer or fraction, results
    # in an IntegerLiteral or FractionalLiteral. Math between literals that
    # results in a float, results in a FloatLiteral().
    value: int | Fraction | float

    @abstractmethod
    def __pos__(self) -> InferrableType:
        pass

    @abstractmethod
    def __neg__(self) -> InferrableType:
        pass

    @abstractmethod
    def __add__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __radd__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __sub__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __rsub__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __mul__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __rmul__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __truediv__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __rtruediv__(self, other: NumericLiteral) -> InferrableType:
        pass

    @abstractmethod
    def __pow__(self, other) -> InferrableType:
        pass

    @abstractmethod
    def __rpow__(self, other) -> InferrableType:
        pass

    @abstractmethod
    def upcast(self) -> DeclarableType:
        pass


@dataclass(frozen=True, slots=True)
class IntegerLiteral(NumericLiteral):
    value: int

    def __pos__(self) -> InferrableType:
        return self

    def __neg__(self) -> InferrableType:
        return IntegerLiteral(-self.value)

    def __add__(self, other: IntegerLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return IntegerLiteral(self.value + value)
            case Integer64():
                return Integer64()
            case _:
                return NotImplemented

    def __radd__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Integer64()
            case _:
                return NotImplemented

    def __sub__(self, other: IntegerLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return IntegerLiteral(self.value - value)
            case Integer64():
                return Integer64()
            case _:
                return NotImplemented

    def __rsub__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Integer64()
            case _:
                return NotImplemented

    def __mul__(self, other: IntegerLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return IntegerLiteral(self.value * value)
            case Integer64():
                return Integer64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __rmul__(self, other: Integer64 | Float64) -> InferrableType:
        match other:
            case Integer64():
                return Integer64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __truediv__(self, other: IntegerLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return FractionalLiteral(Fraction(self.value, value))
            case Integer64():
                return Float64()
            case Float64(right_unit):
                return Float64(Dimensionless() / right_unit)
            case _:
                return NotImplemented

    def __rtruediv__(self, other: Integer64 | Float64) -> InferrableType:
        match other:
            case Integer64():
                return Float64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __pow__(self, other: IntegerLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return FractionalLiteral(Fraction(self.value) ** value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __rpow__(self, other: Integer64) -> InferrableType:
        match other:
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __str__(self) -> str:
        return f"{{{self.value}}}"

    def upcast(self) -> DeclarableType:
        return Integer64()


@dataclass(frozen=True, slots=True)
class FractionalLiteral(NumericLiteral):
    value: Fraction

    def __pos__(self) -> InferrableType:
        return self

    def __neg__(self) -> InferrableType:
        return FractionalLiteral(-self.value)

    def __add__(self, other: IntegerLiteral | FractionalLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FractionalLiteral(self.value + value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __radd__(self, other: IntegerLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return FractionalLiteral(value + self.value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __sub__(self, other: IntegerLiteral | FractionalLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FractionalLiteral(self.value - value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __rsub__(self, other: IntegerLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return FractionalLiteral(value - self.value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __mul__(self, other: IntegerLiteral | FractionalLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FractionalLiteral(self.value * value)
            case Integer64():
                return Float64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __rmul__(self, other: IntegerLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return FractionalLiteral(value * self.value)
            case Integer64():
                return Float64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __truediv__(self, other: IntegerLiteral | FractionalLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FractionalLiteral(self.value / value)
            case Integer64():
                return Float64()
            case Float64(right_unit):
                return Float64(Dimensionless() / right_unit)
            case _:
                return NotImplemented

    def __rtruediv__(self, other: IntegerLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return FractionalLiteral(value / self.value)
            case Integer64():
                return Float64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __pow__(self, other: IntegerLiteral | FractionalLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                return FractionalLiteral(self.value**value)
            case FractionalLiteral(value):
                # Fraction.__pow__ is not type stable
                # It returns a Fraction if it can, otherwise a float
                # Force it to be a float
                return FloatLiteral(float_power(self.value, value))
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __rpow__(self, other: IntegerLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value):
                # Fraction.__rpow__ is not type stable
                # It returns an int if it can, otherwise a float
                # Force it to be a float
                return FloatLiteral(float_power(value, self.value))
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __str__(self) -> str:
        return f"{{{self.value.numerator}/{self.value.denominator}}}"

    def upcast(self) -> DeclarableType:
        return Float64()


@dataclass(frozen=True, slots=True)
class FloatLiteral(NumericLiteral):
    value: float

    def __pos__(self) -> InferrableType:
        return self

    def __neg__(self) -> InferrableType:
        return FloatLiteral(-self.value)

    def __add__(self, other: NumericLiteral | Integer64) -> InferrableType:
        match other:
            case NumericLiteral(value):
                return FloatLiteral(self.value + value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __radd__(self, other: IntegerLiteral | FractionalLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FloatLiteral(value + self.value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __sub__(self, other: NumericLiteral | Integer64) -> InferrableType:
        match other:
            case NumericLiteral(value):
                return FloatLiteral(self.value - value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __rsub__(self, other: IntegerLiteral | FractionalLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FloatLiteral(value - self.value)
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __mul__(self, other: NumericLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case NumericLiteral(value):
                return FloatLiteral(self.value * value)
            case Integer64():
                return Float64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __rmul__(self, other: IntegerLiteral | FractionalLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FloatLiteral(value * self.value)
            case Integer64():
                return Float64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __truediv__(self, other: NumericLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case NumericLiteral(value):
                return FloatLiteral(float_divide(self.value, value))
            case Integer64():
                return Float64()
            case Float64(right_unit):
                return Float64(Dimensionless() / right_unit)
            case _:
                return NotImplemented

    def __rtruediv__(self, other: IntegerLiteral | FractionalLiteral | Integer64 | Float64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FloatLiteral(float_divide(value, self.value))
            case Integer64():
                return Float64()
            case Float64():
                return other
            case _:
                return NotImplemented

    def __pow__(self, other: NumericLiteral | Integer64) -> InferrableType:
        match other:
            case NumericLiteral(value):
                return FloatLiteral(float_power(self.value, value))
            case Integer64():
                return Float64()
            case _:
                return NotImplemented

    def __rpow__(self, other: IntegerLiteral | FractionalLiteral | Integer64) -> InferrableType:
        match other:
            case IntegerLiteral(value) | FractionalLiteral(value):
                return FloatLiteral(float_power(value, self.value))
            case Integer64() | Float64():
                return Float64()
            case _:
                return NotImplemented

    def __eq__(self, other):
        if isinstance(other, FloatLiteral):
            return float_equals(self.value, other.value)
        return NotImplemented

    def __str__(self) -> str:
        return f"{{{self.value}}}"

    def upcast(self) -> DeclarableType:
        return Float64()
