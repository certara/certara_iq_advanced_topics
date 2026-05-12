__all__ = ["free_variables", "free_variable_names"]

from functools import singledispatch

from ordered_set import OrderedSet

from .ast import *


@singledispatch
def free_variables(self: Expression) -> OrderedSet[BaseVariable]:
    """Return set of all free variables in the expression.

    This function walks an expression tree, accumulating the set of free variables that it encounters. This function
    uses single dispatch to recurse on the subexpressions of each node.
    """
    raise NotImplementedError(f"free_variables not implemented for type {type(self).__name__}")


@free_variables.register(BaseVariable)
def free_variables_variable(self: BaseVariable):
    return OrderedSet([self])


@free_variables.register(IntegerLiteral)
@free_variables.register(FloatLiteral)
@free_variables.register(BooleanLiteral)
@free_variables.register(StringLiteral)
def free_variables_literal(self):
    return OrderedSet()


@free_variables.register(ListLiteral)
def free_variables_list_literal(self: ListLiteral):
    result = OrderedSet()
    for element in self.elements:
        result |= free_variables(element)
    return result


@free_variables.register(Positive)
@free_variables.register(Negative)
@free_variables.register(Not)
@free_variables.register(Parentheses)
@free_variables.register(Integral)
def free_variables_unary(self):
    return free_variables(self.contents)


@free_variables.register(Add)
@free_variables.register(Subtract)
@free_variables.register(Multiply)
@free_variables.register(Divide)
@free_variables.register(Power)
@free_variables.register(Equal)
@free_variables.register(NotEqual)
@free_variables.register(GreaterThan)
@free_variables.register(GreaterThanOrEqual)
@free_variables.register(LessThan)
@free_variables.register(LessThanOrEqual)
@free_variables.register(And)
@free_variables.register(Or)
def free_variables_binary(self):
    return free_variables(self.left) | free_variables(self.right)


@free_variables.register(Function)
def free_variables_function(self: Function):
    result = OrderedSet()
    for argument in self.arguments:
        result |= free_variables(argument)
    return result


@free_variables.register(Indexing)
def free_variables_indexing(self: Indexing):
    return free_variables(self.stem) | free_variables(self.index)


@free_variables.register(Convert)
def free_variables_convert(self: Convert):
    return free_variables(self.expression)


@free_variables.register(Maximum)
def free_variables_maximum(self: Maximum):
    return free_variables(self.objective) | free_variables(self.start) | free_variables(self.stop)


@free_variables.register(Ascription)
def free_variables_ascription(self: Ascription):
    return free_variables(self.expression)


def free_variable_names(expression: Expression) -> OrderedSet[str]:
    """Wrapper function for backwards-compatibility; returns variable names and errors on any anonymous variables."""
    names = OrderedSet()
    for variable in free_variables(expression):
        match variable:
            case Variable(name):
                names.add(name)
            case _:
                raise ValueError(f"Unexpected variable {variable} in expression {expression}")
    return names
