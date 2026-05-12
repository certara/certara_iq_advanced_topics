__all__ = ["render"]

import re
from functools import singledispatch

from ..expressions import ast as east
from .ast import *

map = {
    IntegerLiteral: east.IntegerLiteral,
    FloatLiteral: east.FloatLiteral,
    StringLiteral: east.StringLiteral,
    BooleanLiteral: east.BooleanLiteral,
    Positive: east.Positive,
    Negative: east.Negative,
    Not: east.Not,
    Parentheses: east.Parentheses,
    Integral: east.Integral,
    Add: east.Add,
    Subtract: east.Subtract,
    Multiply: east.Multiply,
    Divide: east.Divide,
    Power: east.Power,
    Equal: east.Equal,
    NotEqual: east.NotEqual,
    GreaterThan: east.GreaterThan,
    GreaterThanOrEqual: east.GreaterThanOrEqual,
    LessThan: east.LessThan,
    LessThanOrEqual: east.LessThanOrEqual,
    Or: east.Or,
    And: east.And,
    Function: east.Function,
}


@singledispatch
def render(self, index_map: dict[str | int, int]) -> east.Expression:
    """Render a templated expression into a concrete expression AST."""

    raise NotImplementedError(f"render not implemented for type {type(self).__name__}")


@render.register(IntegerLiteral)
@render.register(FloatLiteral)
@render.register(StringLiteral)
@render.register(BooleanLiteral)
def render_literal(self, index_map: dict[str | int, int]):
    return map[type(self)](self.value)


@render.register(TemplatedVariable)
def render_templated_variable(self: TemplatedVariable, index_map: dict[str | int, int]):
    rendered_name = self.name.render(index_map)
    if re.fullmatch(r"\d+", rendered_name):
        return east.IntegerLiteral(int(rendered_name))
    if re.fullmatch(r"\d+((\.\d+([Ee][+-]?\d+)?)|((\.\d+)?[Ee][+-]?\d+))", rendered_name):
        return east.FloatLiteral(float(rendered_name))
    return east.Variable(rendered_name)


@render.register(TemplatedFunctionSum)
def render_templated_function_sum(self: TemplatedFunctionSum, index_map: dict[str | int, int]):
    from ..templated_reaction.render_template.generate_index_maps import generate_index_maps

    free_label_lengths = self.free_label_length(self.labels)
    label_map = generate_index_maps(free_label_lengths)

    if len(label_map) == 0:
        # Exit early if there is nothing to sum
        # This looks nicer than reducing with a 0 starting element
        return east.IntegerLiteral(0)

    all_terms = []
    for local_label_map in label_map:
        new_variable = render(self.templated_expression, local_label_map | index_map)
        all_terms.append(new_variable)
    add_exp = all_terms[0]
    for i in range(1, len(all_terms)):
        add_exp = east.Add(add_exp, all_terms[i])
    return add_exp


@render.register(TemplatedFunctionMean)
def render_templated_function_mean(self: TemplatedFunctionMean, index_map: dict[str | int, int]):
    from ..templated_reaction.render_template.generate_index_maps import generate_index_maps

    free_label_lengths = self.free_label_length(self.labels)
    label_map = generate_index_maps(free_label_lengths)

    if len(label_map) == 0:
        # Cannot compute mean of 0 terms
        raise ZeroDivisionError(f"Cannot compute mean of 0 terms in template {self}")

    all_terms = []
    for local_label_map in label_map:
        new_variable = render(self.templated_expression, local_label_map | index_map)
        all_terms.append(new_variable)
    add_exp = all_terms[0]
    for i in range(1, len(all_terms)):
        add_exp = east.Add(add_exp, all_terms[i])

    return east.Divide(add_exp, east.FloatLiteral(float(len(all_terms))))


@render.register(Positive)
@render.register(Negative)
@render.register(Not)
@render.register(Parentheses)
@render.register(Integral)
def render_contents(self, index_map: dict[str | int, int]):
    return map[type(self)](render(self.contents, index_map))


@render.register(Add)
@render.register(Subtract)
@render.register(Multiply)
@render.register(Divide)
@render.register(Power)
@render.register(Equal)
@render.register(NotEqual)
@render.register(GreaterThan)
@render.register(GreaterThanOrEqual)
@render.register(LessThan)
@render.register(LessThanOrEqual)
@render.register(Or)
@render.register(And)
def render_left_right(self, index_map: dict[str | int, int]):
    return map[type(self)](render(self.left, index_map), render(self.right, index_map))


@render.register(Function)
def render_function(self: Function, index_map: dict[str | int, int]):
    return map[type(self)](self.name, [render(argument, index_map) for argument in self.arguments])


@render.register(Indexing)
def render_indexing(self: Indexing, index_map: dict[str | int, int]):
    return east.Indexing(render(self.stem, index_map), render(self.index, index_map))


@render.register(Maximum)
def render_maximum(self: Maximum, index_map: dict[str | int, int]):
    return east.Maximum(
        render(self.objective, index_map),
        render(self.start, index_map),
        render(self.stop, index_map),
    )


@render.register(Ascription)
def render_ascription(self: Ascription, index_map: dict[str | int, int]):
    return east.Ascription(render(self.expression, index_map), self.type)


@render.register(Convert)
def render_convert(self: Convert, index_map: dict[str | int, int]):
    return east.Convert(render(self.expression, index_map), self.from_unit, self.to_unit)
