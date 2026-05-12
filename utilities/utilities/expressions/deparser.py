__all__ = ["deparse_expression"]

from functools import singledispatch

from ..types import ast as tast
from ..types import deparse_type
from ..units import ast as uast
from ..units import deparse_unit
from .ast import *


@singledispatch
def deparse_expression(self) -> str:
    raise NotImplementedError(f"deparse_expression not implemented for type {type(self).__name__}")


@deparse_expression.register(IntegerLiteral)
@deparse_expression.register(FloatLiteral)
def deparse_expression_simple_literal(self):
    return repr(self.value)


@deparse_expression.register(StringLiteral)
def deparse_expression_string_literal(self: StringLiteral):
    return repr(self.value)


@deparse_expression.register(BooleanLiteral)
def deparse_expression_boolean_literal(self: BooleanLiteral):
    if self.value:
        return "true"
    else:
        return "false"


@deparse_expression.register(ListLiteral)
def deparse_expression_list_literal(self: ListLiteral):
    return f"[{', '.join(map(deparse_expression, self.elements))}]"


@deparse_expression.register(Variable)
def deparse_expression_variable(self: Variable):
    return self.name


@deparse_expression.register(Positive)
def deparse_expression_positive(self: Positive):
    if isinstance(self.contents, (Add, Subtract, Multiply, Divide)):
        return f"+({deparse_expression(self.contents)})"
    else:
        return f"+{deparse_expression(self.contents)}"


@deparse_expression.register(Negative)
def deparse_expression_negative(self: Negative):
    if isinstance(self.contents, (Add, Subtract, Multiply, Divide)):
        return f"-({deparse_expression(self.contents)})"
    else:
        return f"-{deparse_expression(self.contents)}"


@deparse_expression.register(Add)
def deparse_expression_add(self: Add):
    return f"{deparse_expression(self.left)} + {deparse_expression(self.right)}"


@deparse_expression.register(Subtract)
def deparse_expression_subtract(self: Subtract):
    if isinstance(self.right, (Add, Subtract)):
        right_string = f"({deparse_expression(self.right)})"
    else:
        right_string = deparse_expression(self.right)

    return f"{deparse_expression(self.left)} - {right_string}"


@deparse_expression.register(Multiply)
def deparse_expression_multiply(self: Multiply):
    if isinstance(self.left, (Add, Subtract)):
        left_string = f"({deparse_expression(self.left)})"
    else:
        left_string = deparse_expression(self.left)

    if isinstance(self.right, (Add, Subtract)):
        right_string = f"({deparse_expression(self.right)})"
    else:
        right_string = deparse_expression(self.right)

    return f"{left_string} * {right_string}"


@deparse_expression.register(Divide)
def deparse_expression_divide(self: Divide):
    if isinstance(self.left, (Add, Subtract)):
        left_string = f"({deparse_expression(self.left)})"
    else:
        left_string = deparse_expression(self.left)

    if isinstance(self.right, (Add, Subtract, Multiply, Divide)):
        right_string = f"({deparse_expression(self.right)})"
    else:
        right_string = deparse_expression(self.right)

    return f"{left_string} / {right_string}"


@deparse_expression.register(Power)
def deparse_expression_power(self: Power):
    if isinstance(self.left, (Add, Subtract, Multiply, Divide, Power)):
        left_string = f"({deparse_expression(self.left)})"
    else:
        left_string = deparse_expression(self.left)

    if isinstance(self.right, (Add, Subtract, Multiply, Divide)):
        right_string = f"({deparse_expression(self.right)})"
    else:
        right_string = deparse_expression(self.right)

    return f"{left_string} ^ {right_string}"


@deparse_expression.register(Equal)
def deparse_expression_equal(self: Equal):
    return f"{deparse_expression(self.left)} == {deparse_expression(self.right)}"


@deparse_expression.register(NotEqual)
def deparse_expression_not_equal(self: NotEqual):
    return f"{deparse_expression(self.left)} != {deparse_expression(self.right)}"


@deparse_expression.register(GreaterThan)
def deparse_expression_greater_than(self: GreaterThan):
    return f"{deparse_expression(self.left)} > {deparse_expression(self.right)}"


@deparse_expression.register(GreaterThanOrEqual)
def deparse_expression_greater_than_or_equal(self: GreaterThanOrEqual):
    return f"{deparse_expression(self.left)} >= {deparse_expression(self.right)}"


@deparse_expression.register(LessThan)
def deparse_expression_less_than(self: LessThan):
    return f"{deparse_expression(self.left)} < {deparse_expression(self.right)}"


@deparse_expression.register(LessThanOrEqual)
def deparse_expression_less_than_or_equal(self: LessThanOrEqual):
    return f"{deparse_expression(self.left)} <= {deparse_expression(self.right)}"


@deparse_expression.register(Or)
def deparse_expression_or(self: Or):
    return f"{deparse_expression(self.left)} || {deparse_expression(self.right)}"


@deparse_expression.register(And)
def deparse_expression_and(self: And):
    if isinstance(self.left, Or):
        left_string = f"({deparse_expression(self.left)})"
    else:
        left_string = deparse_expression(self.left)

    if isinstance(self.right, Or):
        right_string = f"({deparse_expression(self.right)})"
    else:
        right_string = deparse_expression(self.right)

    return f"{left_string} && {right_string}"


@deparse_expression.register(Not)
def deparse_expression_not(self: Not):
    if isinstance(self.contents, (Or, And)):
        return f"!({deparse_expression(self.contents)})"
    else:
        return f"!{deparse_expression(self.contents)}"


@deparse_expression.register(Parentheses)
def deparse_expression_parentheses(self: Parentheses):
    return f"({deparse_expression(self.contents)})"


@deparse_expression.register(Function)
def deparse_expression_function(self: Function):
    return f"{self.name}({', '.join(map(str, self.arguments))})"


@deparse_expression.register(Indexing)
def deparse_expression_indexing(self: Indexing):
    if isinstance(self.stem, (Add, Subtract, Multiply, Divide, Power)):
        stem_string = f"({deparse_expression(self.stem)})"
    else:
        stem_string = deparse_expression(self.stem)

    return f"{stem_string}[{deparse_expression(self.index)}]"


@deparse_expression.register(Concatenate)
def deparse_expression_concatinate(self: Concatenate):
    return f"{deparse_expression(self.left)} ++ {deparse_expression(self.right)}"


@deparse_expression.register(Ascription)
def deparse_expression_ascription(self: Ascription):
    match self.expression:
        case Add() | Subtract() | Multiply() | Divide() | Power():
            expression_string = f"({deparse_expression(self.expression)})"
        case _:
            expression_string = deparse_expression(self.expression)

    match self.type:
        case tast.Float64(unit):
            # Deparse Float64[_] back into bare unit ascription syntax.  Note we need to wrap compound units.
            match unit:
                case uast.Multiply() | uast.Divide() | uast.Power():
                    type_string = f"({deparse_unit(unit)})"
                case _:
                    type_string = deparse_unit(unit)
        case _:  # All other types
            type_string = deparse_type(self.type)

    return f"{expression_string}:{type_string}"


@deparse_expression.register(Convert)
def deparse_expression_convert(self: Convert):
    return (
        f"convert({deparse_expression(self.expression)}, {deparse_unit(self.from_unit)}, {deparse_unit(self.to_unit)})"
    )
