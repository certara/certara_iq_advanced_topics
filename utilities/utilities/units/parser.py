__all__ = ["parse_unit", "un", "UnitParsers"]

from fractions import Fraction
from operator import neg
from typing import List

from parsita import ParserContext, Result, lit, opt, pred, reg, rep
from parsita.util import constant, splat

from .ast import Atom, Dimensionless, Divide, Dynamic, Multiply, Parenthesis, Power, Unit
from .valid_units import valid_units

valid_units_error_string = " or ".join(valid_units.keys())


def make_power(base: Unit, maybe_exponent: List[int]):
    if len(maybe_exponent) == 0:
        return base
    else:
        return Power(base, maybe_exponent[0])


def make_compound(first, rest):
    value = first
    for op, term in rest:
        if op == "*":
            value = Multiply(value, term)
        else:
            value = Divide(value, term)
    return value


class UnitParsers(ParserContext, whitespace=r"[ \t]*"):
    """Parsita grammar for ReactionModel unit expressions."""

    dimensionless = lit("1") > constant(Dimensionless())
    atom = pred(reg(r"[A-Za-z_][A-Za-z_0-9]*"), lambda x: x in valid_units, valid_units_error_string) > Atom
    parenthesis = "(" >> compound << ")" > Parenthesis  # noqa: F821

    single = dimensionless | atom | parenthesis

    whole = reg(r"\d+") > int
    natural = pred(whole, lambda x: x != 0, "positive integer")
    integer = opt("+") >> whole | ("-" >> whole > neg)
    fraction = "(" >> integer << "/" & natural << ")" > splat(Fraction)
    exponent = integer | fraction
    power = single & opt("^" >> exponent) > splat(make_power)
    compound = power & rep(lit("*", "/") & power) > splat(make_compound)

    dynamic = lit("dynamic") > constant(Dynamic())

    unit = dynamic | compound


def parse_unit(text: str) -> Result[Unit]:
    """Parse ReactionModel unit text such as ``nM`` or ``nmol/L``."""

    return UnitParsers.unit.parse(text)


def un(text: str) -> Unit:
    """Parse unit text and return the unit AST, raising on invalid input."""

    return parse_unit(text).unwrap()
