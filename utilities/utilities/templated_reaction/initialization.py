__all__ = ["TemplatedInitialization", "TemplatedInitialValue", "TemplatedSteadyState"]


from dataclasses import dataclass

from ..templated_expressions import TemplatedExpression


class TemplatedInitialization:
    """Base class for templated model initialization settings."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class TemplatedInitialValue(TemplatedInitialization):
    """Initialize the rendered model from declared state initial values."""


@dataclass(frozen=True, slots=True)
class TemplatedSteadyState(TemplatedInitialization):
    """Initialize the rendered model by solving to steady state."""

    time_scale: TemplatedExpression
    max_time: TemplatedExpression | None = None
