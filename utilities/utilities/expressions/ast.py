__all__ = [
    "Expression",
    "StringLiteral",
    "IntegerLiteral",
    "FloatLiteral",
    "BooleanLiteral",
    "ListLiteral",
    "BaseVariable",
    "Variable",
    "AnonymousVariable",
    "Positive",
    "Negative",
    "Add",
    "Subtract",
    "Multiply",
    "Divide",
    "Power",
    "Equal",
    "NotEqual",
    "GreaterThan",
    "GreaterThanOrEqual",
    "LessThan",
    "LessThanOrEqual",
    "Or",
    "And",
    "Not",
    "Parentheses",
    "Function",
    "Indexing",
    "KroneckerDelta",
    "Integral",
    "Maximum",
    "Concatenate",
    "Ascription",
    "Convert",
]

from dataclasses import dataclass

from ..types import DeclarableType
from ..units import Unit


@dataclass(frozen=True, slots=True)
class Expression:
    def __str__(self):
        from .deparser import deparse_expression

        return deparse_expression(self)

    def __add__(self, other):
        if not isinstance(other, Expression):
            return NotImplemented
        return Add(self, other)

    def __radd__(self, other):
        if not isinstance(other, Expression):
            return NotImplemented
        return Add(other, self)

    def __mul__(self, other):
        if not isinstance(other, Expression):
            return NotImplemented
        return Multiply(self, other)

    def __rmul__(self, other):
        if not isinstance(other, Expression):
            return NotImplemented
        return Multiply(other, self)


@dataclass(frozen=True, slots=True)
class BooleanLiteral(Expression):
    value: bool


@dataclass(frozen=True, slots=True)
class IntegerLiteral(Expression):
    value: int


@dataclass(frozen=True, slots=True)
class FloatLiteral(Expression):
    value: float


@dataclass(frozen=True, slots=True)
class StringLiteral(Expression):
    value: str


@dataclass(frozen=True, slots=True)
class ListLiteral(Expression):
    elements: list[Expression]

    def __hash__(self):
        return hash(tuple(self.elements))


@dataclass(frozen=True, slots=True)
class BaseVariable(Expression):
    pass


@dataclass(frozen=True, slots=True)
class AnonymousVariable(BaseVariable):
    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return f"AnonymousVariable(id={id(self)})"


@dataclass(frozen=True, slots=True)
class Variable(BaseVariable):
    name: str


@dataclass(frozen=True, slots=True)
class Positive(Expression):
    contents: Expression


@dataclass(frozen=True, slots=True)
class Negative(Expression):
    contents: Expression


@dataclass(frozen=True, slots=True)
class Add(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Subtract(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Multiply(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Divide(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Power(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Equal(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class NotEqual(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class GreaterThan(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class GreaterThanOrEqual(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class LessThan(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class LessThanOrEqual(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Or(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class And(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Not(Expression):
    contents: Expression


@dataclass(frozen=True, slots=True)
class Parentheses(Expression):
    contents: Expression


@dataclass(frozen=True, slots=True)
class Function(Expression):
    name: str
    arguments: list[Expression]

    def __hash__(self):
        return hash((self.name, tuple(self.arguments)))


@dataclass(frozen=True, slots=True)
class Indexing(Expression):
    stem: Expression
    index: Expression


@dataclass(frozen=True, slots=True)
class KroneckerDelta(Expression):
    location: Expression


@dataclass(frozen=True, slots=True)
class Integral(Expression):
    contents: Expression


@dataclass(frozen=True, slots=True)
class Maximum(Expression):
    objective: Expression
    start: Expression
    stop: Expression


@dataclass(frozen=True, slots=True)
class Concatenate(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Ascription(Expression):
    expression: Expression
    type: DeclarableType


@dataclass(frozen=True, slots=True)
class Convert(Expression):
    expression: Expression
    from_unit: Unit
    to_unit: Unit
