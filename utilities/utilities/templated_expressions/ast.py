from __future__ import annotations

__all__ = [
    "TemplatedExpression",
    "StringLiteral",
    "IntegerLiteral",
    "FloatLiteral",
    "BooleanLiteral",
    "ListLiteral",
    "TemplatedVariable",
    "BaseTemplatedFunction",
    "TemplatedFunctionSum",
    "TemplatedFunctionMean",
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

from dataclasses import dataclass, replace

from ..types import DeclarableType
from ..units import Unit
from .templated_name import TemplatedName


@dataclass(frozen=True, slots=True)
class TemplatedExpression:
    def __str__(self):
        from .deparser import deparse_expression

        return deparse_expression(self)

    def __add__(self, other):
        if not isinstance(other, TemplatedExpression):
            return NotImplemented
        return Add(self, other)

    def __radd__(self, other):
        if not isinstance(other, TemplatedExpression):
            return NotImplemented
        return Add(other, self)

    def __mul__(self, other):
        if not isinstance(other, TemplatedExpression):
            return NotImplemented
        return Multiply(self, other)

    def __rmul__(self, other):
        if not isinstance(other, TemplatedExpression):
            return NotImplemented
        return Multiply(other, self)


@dataclass(frozen=True, slots=True)
class BooleanLiteral(TemplatedExpression):
    value: bool


@dataclass(frozen=True, slots=True)
class IntegerLiteral(TemplatedExpression):
    value: int


@dataclass(frozen=True, slots=True)
class FloatLiteral(TemplatedExpression):
    value: float


@dataclass(frozen=True, slots=True)
class StringLiteral(TemplatedExpression):
    value: str


@dataclass(frozen=True, slots=True)
class ListLiteral(TemplatedExpression):
    elements: list[TemplatedExpression]

    def __hash__(self):
        return hash(tuple(self.elements))


@dataclass(frozen=True, slots=True)
class TemplatedVariable(TemplatedExpression):
    name: TemplatedName

    def free_label_length(self, labels: list[int]):
        label_length_map = {}
        for label in labels:
            for interpolation in self.name.interpolations:
                if interpolation.label == label:
                    label_length_map[label] = len(interpolation.variables)
        return label_length_map

    def validate(
        self,
        globals: dict[str, list[str]],
        global_variable_implicit_label_map: dict[str, str],
        generated_label: str,
        implicit_label_local_variables_map: dict[str, list[str | int]],
        label_value_list_length_map: dict[int | str, int],
        function_labels: list[int] = [],
    ) -> tuple[
        dict[str, str],
        str,
        dict[str, list[str | int]],
        dict[int | str, int],
        TemplatedVariable,
    ]:
        (
            global_variable_implicit_label_map,
            generated_label,
            implicit_label_local_variables_map,
            label_value_list_length_map,
            updated_templte_name,
        ) = self.name.validate(
            globals,
            global_variable_implicit_label_map,
            generated_label,
            implicit_label_local_variables_map,
            label_value_list_length_map,
            function_labels,
        )

        updated_templated_variable = replace(self, name=updated_templte_name)

        return (
            global_variable_implicit_label_map,
            generated_label,
            implicit_label_local_variables_map,
            label_value_list_length_map,
            updated_templated_variable,
        )


@dataclass(frozen=True, slots=True)
class BaseTemplatedFunction(TemplatedExpression):
    templated_expression: TemplatedExpression
    labels: list[int]

    def __hash__(self):
        # Create a hash based on immutable attributes
        return hash((self.templated_expression, tuple(self.labels)))

    def free_label_length(self, labels: list[int]):
        from . import free_variable_names

        label_length_map = {}
        variables = free_variable_names(self.templated_expression)
        for variable in variables:
            label_length_map |= variable.free_label_length(self.labels + labels)
        return label_length_map

    def validate(
        self,
        globals: dict[str, list[str]],
        global_variable_implicit_label_map: dict[str, str],
        generated_label: str,
        implicit_label_local_variables_map: dict[str, list[str | int]],
        label_value_list_length_map: dict[int | str, int],
    ) -> tuple[
        dict[str, str],
        str,
        dict[str, list[str | int]],
        dict[int | str, int],
        BaseTemplatedFunction,
    ]:
        from . import free_variable_names, substitute

        expression_map = {}
        variables = free_variable_names(self.templated_expression)
        for variable in variables:
            (
                global_variable_implicit_label_map,
                generated_label,
                implicit_label_local_variables_map,
                label_value_list_length_map,
                updated_variable,
            ) = variable.validate(
                globals,
                global_variable_implicit_label_map,
                generated_label,
                implicit_label_local_variables_map,
                label_value_list_length_map,
                self.labels,
            )
            expression_map[variable] = updated_variable
        updated_expression = substitute(self.templated_expression, expression_map)
        updated_function = replace(self, templated_expression=updated_expression)
        return (
            global_variable_implicit_label_map,
            generated_label,
            implicit_label_local_variables_map,
            label_value_list_length_map,
            updated_function,
        )


@dataclass(frozen=True, eq=False)
class TemplatedFunctionSum(BaseTemplatedFunction):
    pass


@dataclass(frozen=True, eq=False)
class TemplatedFunctionMean(BaseTemplatedFunction):
    pass


@dataclass(frozen=True, slots=True)
class Positive(TemplatedExpression):
    contents: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Negative(TemplatedExpression):
    contents: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Add(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Subtract(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Multiply(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Divide(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Power(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Equal(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class NotEqual(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class GreaterThan(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class GreaterThanOrEqual(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class LessThan(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class LessThanOrEqual(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Or(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class And(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Not(TemplatedExpression):
    contents: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Parentheses(TemplatedExpression):
    contents: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Function(TemplatedExpression):
    name: str
    arguments: list[TemplatedExpression]

    def __hash__(self):
        return hash((self.name, tuple(self.arguments)))


@dataclass(frozen=True, slots=True)
class Indexing(TemplatedExpression):
    stem: TemplatedExpression
    index: TemplatedExpression


@dataclass(frozen=True, slots=True)
class KroneckerDelta(TemplatedExpression):
    location: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Integral(TemplatedExpression):
    contents: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Maximum(TemplatedExpression):
    objective: TemplatedExpression
    start: TemplatedExpression
    stop: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Concatenate(TemplatedExpression):
    left: TemplatedExpression
    right: TemplatedExpression


@dataclass(frozen=True, slots=True)
class Ascription(TemplatedExpression):
    expression: TemplatedExpression
    type: DeclarableType


@dataclass(frozen=True, slots=True)
class Convert(TemplatedExpression):
    expression: TemplatedExpression
    from_unit: Unit
    to_unit: Unit
