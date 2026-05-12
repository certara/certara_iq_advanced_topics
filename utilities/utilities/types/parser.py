__all__ = ["TypeParsers", "parse_type", "dtype"]

from parsita import Failure, ParserContext, Result, Success, lit
from parsita.util import constant

from ..units.parser import UnitParsers, parse_unit
from .ast import Array, Boolean, DataType, Dynamic, Float64, InferrableType, Integer64, Nothing, String


class TypeParsers(ParserContext):
    """Parsita grammar for ReactionModel declarable types."""

    boolean = lit("Boolean") > constant(Boolean())
    integer = lit("Integer64") > constant(Integer64())
    float64 = lit("Float64") > constant(Float64())
    unitted = lit("Float64") >> "[" >> UnitParsers.unit << "]" > Float64
    string = lit("String") > constant(String())

    data_type = boolean | integer | unitted | float64 | string

    nothing = lit("Nothing") > constant(Nothing())

    proper_type = data_type | nothing

    dynamic = lit("dynamic") > constant(Dynamic())

    array = lit("Array") >> "[" >> (data_type | nothing | dynamic) << "]" > Array

    declarable_type = data_type | array | nothing | dynamic


def parse_type(text: str) -> Result[DataType]:
    """Parse ReactionModel type text such as ``Float64[nM]`` or ``Array[String]``."""

    return TypeParsers.declarable_type.parse(text)


def dtype(value: InferrableType | str) -> InferrableType:
    """Return a type AST from an existing type, type string, or unit string."""

    match value:
        case InferrableType():
            return value
        case str():
            match parse_type(value):
                case Success(data_type):
                    return data_type
                case Failure(error):
                    match parse_unit(value):
                        case Success(unit):
                            return Float64(unit)
                        case Failure(_):
                            # Raise the type error if both fail
                            raise error
