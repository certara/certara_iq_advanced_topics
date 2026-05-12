__all__ = ["ExpressionParsers", "parse_expression", "reserved_names", "ex"]

from functools import reduce

from parsita import ParserContext, Result, lit, opt, pred, reg, rep, rep1sep, repsep
from parsita.util import constant, splat

from ..types import TypeParsers
from ..types.ast import Float64
from ..units.parser import UnitParsers
from .ast import *


def make_exponent(first, maybe_second):
    if len(maybe_second) == 0:
        return first
    else:
        return Power(first, maybe_second[0])


def make_indexing(first, rest):
    value = first
    for term in rest:
        value = Indexing(value, term)
    return value


def make_ascription(first, maybe_second):
    if len(maybe_second) == 0:
        return first
    else:
        return Ascription(first, maybe_second[0])


def make_term(first, rest):
    value = first
    for op, term in rest:
        if op == "*":
            value = Multiply(value, term)
        else:
            value = Divide(value, term)
    return value


def make_numeric_expression(first, rest):
    value = first
    for op, term in rest:
        if op == "+":
            value = Add(value, term)
        elif op == "-":
            value = Subtract(value, term)
        elif op == "++":
            value = Concatenate(value, term)
        else:
            raise NotImplementedError
    return value


def make_comparison_expression(first, maybe_second):
    if len(maybe_second) == 0:
        return first
    else:
        op, second = maybe_second[0]
        if op == "==":
            return Equal(first, second)
        elif op == "!=":
            return NotEqual(first, second)
        elif op == ">=":
            return GreaterThanOrEqual(first, second)
        elif op == "<=":
            return LessThanOrEqual(first, second)
        elif op == ">":
            return GreaterThan(first, second)
        elif op == "<":
            return LessThan(first, second)
        else:
            raise NotImplementedError


reserved_names = {"true", "false", "inf", "nan", "null"}


class ExpressionParsers(ParserContext, whitespace=r"[ \t]*"):
    # Atoms
    true = lit("true", "True") > constant(BooleanLiteral(True))
    false = lit("false", "False") > constant(BooleanLiteral(False))
    boolean_literal = true | false

    float_literal = reg(r"\d+((\.\d+([Ee][+-]?\d+)?)|((\.\d+)?[Ee][+-]?\d+))") | reg(r"\binf\b") | reg(r"\bnan\b") > (
        lambda x: FloatLiteral(float(x))
    )
    integer_literal = reg(r"\d+") > (lambda x: IntegerLiteral(int(x)))
    numeric_literal = float_literal | integer_literal

    string_literal = reg(r"'[^']*'") > (lambda x: StringLiteral(x[1:-1]))

    list_literal = "[" >> repsep(expression, ",") << "]" > ListLiteral

    name = pred(reg(r"[A-Za-z_][A-Za-z_0-9]*"), lambda x: x not in reserved_names, "non-keyword")

    variable = name > Variable

    function_name = pred(reg(r"[A-Za-z_][A-Za-z_0-9]*"), lambda x: x not in reserved_names, "non-keyword")

    convert = "convert(" >> expression << "," & UnitParsers.unit << "," & UnitParsers.unit << ")" > splat(Convert)

    function = function_name & "(" >> repsep(expression, ",") << ")" > splat(Function)

    parentheses = "(" >> expression << ")" > Parentheses

    atom = (
        boolean_literal
        | float_literal
        | integer_literal
        | string_literal
        | list_literal
        | convert
        | function
        | variable
        | parentheses
    )

    # Indexing
    indexing = atom & rep("[" >> expression << "]") > splat(make_indexing)

    # Type ascription
    single_unit_type = UnitParsers.single > (lambda u: Float64(u))
    ascription = indexing & opt(":" >> (TypeParsers.declarable_type | single_unit_type)) > splat(make_ascription)

    # Numeric operators
    negative = "-" >> factor > Negative
    positive = "+" >> factor > Positive
    exponent = ascription & opt("^" >> factor) > splat(make_exponent)
    factor = negative | positive | exponent

    # Left-recursion must be handled manually as a parser combinator will stack overflow
    # + - * / are all left-recursive because they are left-associative operators
    term = factor & rep(lit("*", "/") & factor) > splat(make_term)
    numeric_expression = term & rep(lit("++", "+", "-") & term) > splat(make_numeric_expression)

    # Comparison operators
    comparison_expression = numeric_expression & opt(
        lit("==", "!=", ">=", "<=", ">", "<") & numeric_expression
    ) > splat(make_comparison_expression)

    # Boolean operators
    not_expression = "!" >> unary_boolean > Not

    unary_boolean = not_expression | comparison_expression

    # Left-recursion must be handled manually as a parser combinator will stack overflow
    # && and || are both left-recursive because they are left-associative operators
    and_expression = rep1sep(unary_boolean, "&&") > (lambda x: reduce(And, x))
    expression = rep1sep(and_expression, "||") > (lambda x: reduce(Or, x))


def parse_expression(text: str) -> Result[Expression]:
    """Parse concrete ReactionModel expression text into an expression AST."""

    return ExpressionParsers.expression.parse(text)


def ex(text: bool | int | float | str) -> Expression:
    """Convert Python data or concrete expression text into an expression AST."""

    match text:
        case bool():
            return BooleanLiteral(text)
        case int():
            return IntegerLiteral(text)
        case float():
            return FloatLiteral(text)
        case _:
            return parse_expression(text).unwrap()
