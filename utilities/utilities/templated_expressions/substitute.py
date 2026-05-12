__all__ = ["substitute"]

from functools import singledispatch
from typing import Dict

from .ast import *


@singledispatch
def substitute(self, replacements: Dict[str, TemplatedExpression]) -> TemplatedExpression:
    raise NotImplementedError(f"substitute not implemented for type {type(self).__name__}")


@substitute.register(IntegerLiteral)
@substitute.register(FloatLiteral)
@substitute.register(StringLiteral)
@substitute.register(BooleanLiteral)
def substitute_literal(self, replacements):
    return self


@substitute.register(BaseTemplatedFunction)
@substitute.register(TemplatedVariable)
def substitute_variable(self: TemplatedVariable, replacements: Dict[str, TemplatedExpression]):
    return replacements.get(self, self)


@substitute.register(Positive)
@substitute.register(Negative)
@substitute.register(Not)
@substitute.register(Parentheses)
@substitute.register(Integral)
def substitute_contents(self, replacements: Dict[str, TemplatedExpression]):
    return type(self)(substitute(self.contents, replacements))


@substitute.register(Add)
@substitute.register(Subtract)
@substitute.register(Multiply)
@substitute.register(Divide)
@substitute.register(Power)
@substitute.register(Equal)
@substitute.register(NotEqual)
@substitute.register(GreaterThan)
@substitute.register(GreaterThanOrEqual)
@substitute.register(LessThan)
@substitute.register(LessThanOrEqual)
@substitute.register(Or)
@substitute.register(And)
def substitute_left_right(self, replacements: Dict[str, TemplatedExpression]):
    return type(self)(substitute(self.left, replacements), substitute(self.right, replacements))


@substitute.register(Function)
def substitute_function(self: Function, replacements: Dict[str, TemplatedExpression]):
    return type(self)(self.name, [substitute(argument, replacements) for argument in self.arguments])


@substitute.register(Indexing)
def substitute_indexing(self: Indexing, replacements: Dict[str, TemplatedExpression]):
    return Indexing(substitute(self.stem, replacements), substitute(self.index, replacements))


@substitute.register(Maximum)
def substitute_maximum(self: Maximum, replacements: Dict[str, TemplatedExpression]):
    return Maximum(
        substitute(self.objective, replacements),
        substitute(self.start, replacements),
        substitute(self.stop, replacements),
    )


@substitute.register(Ascription)
def substitute_ascription(self: Ascription, replacements: Dict[str, TemplatedExpression]):
    return Ascription(substitute(self.expression, replacements), self.type)


@substitute.register(Convert)
def substitute_convert(self: Convert, replacements: Dict[str, TemplatedExpression]):
    return Convert(substitute(self.expression, replacements), self.from_unit, self.to_unit)
