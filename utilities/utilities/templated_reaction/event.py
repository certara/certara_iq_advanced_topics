__all__ = ["TemplatedEvent"]

from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression


@dataclass(frozen=True, slots=True)
class TemplatedEvent:
    """A templated event with a trigger expression and one or more effects."""

    trigger: TemplatedExpression
    effects: dict[str, TemplatedExpression]
