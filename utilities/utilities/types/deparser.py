__all__ = ["deparse_type"]

from functools import singledispatch

from ..units import deparse_unit
from ..units.ast import Dimensionless
from .ast import Array, Boolean, DeclarableType, Dynamic, Float64, Integer64, Nothing, String


@singledispatch
def deparse_type(self: DeclarableType) -> str:
    raise NotImplementedError(f"deparse_type not implemented for type {type(self).__name__}")


@deparse_type.register(Dynamic)
def deparse_type_dynamic(self: Dynamic) -> str:
    return "dynamic"


@deparse_type.register(Boolean)
def deparse_type_boolean(self: Boolean) -> str:
    return "Boolean"


@deparse_type.register(Integer64)
def deparse_type_integer(self: Integer64) -> str:
    return "Integer64"


@deparse_type.register(Float64)
def deparse_type_float64(self: Float64) -> str:
    match self.unit:
        case Dimensionless():
            return "Float64"
        case _:
            return f"Float64[{deparse_unit(self.unit)}]"


@deparse_type.register(String)
def deparse_type_string(self: String) -> str:
    return "String"


@deparse_type.register(Array)
def deparse_type_array(self: Array) -> str:
    return f"Array[{deparse_type(self.element_type)}]"


@deparse_type.register(Nothing)
def deparse_type_nothing(self: Nothing) -> str:
    return "Nothing"
