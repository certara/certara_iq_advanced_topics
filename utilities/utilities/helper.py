__all__ = ["is_static", "or_else", "make_steady_state"]

from typing import Callable, Tuple, TypeVar

from .expressions import Expression
from .expressions import free_variable_names as free_expression_variable_names
from .reaction.initialization import SteadyState
from .templated_expressions import TemplatedExpression, free_variable_names
from .templated_reaction.initialization import TemplatedInitialization, TemplatedSteadyState

Value = TypeVar("Value")
Default = TypeVar("Default")


def is_static(expression: Expression | TemplatedExpression):
    match expression:
        case Expression():
            extra_variables = free_expression_variable_names(expression)
        case TemplatedExpression():
            extra_variables = free_variable_names(expression)
        case _:
            raise ValueError(f"Unexpected expression type: {type(expression)}")
    return len(extra_variables) == 0


def or_else(default: Default) -> Callable[[Tuple[()] | Tuple[TemplatedInitialization]], Value | Default]:
    def or_else_inner(maybe_value: Tuple[()] | Tuple[TemplatedInitialization]) -> Value | Default:
        if len(maybe_value) != 0:
            return maybe_value[0]
        else:
            return default

    return or_else_inner


def make_steady_state(time_scale: TemplatedExpression, maybe_max_time: Tuple[()] | Tuple[TemplatedExpression]):
    if len(maybe_max_time) == 0:
        return TemplatedSteadyState(time_scale)
    else:
        return TemplatedSteadyState(time_scale, maybe_max_time[0])


def make_reaction_steady_state(time_scale: Expression, maybe_max_time: Tuple[()] | Tuple[Expression]):
    if len(maybe_max_time) == 0:
        return SteadyState(time_scale)
    else:
        return SteadyState(time_scale, maybe_max_time[0])
