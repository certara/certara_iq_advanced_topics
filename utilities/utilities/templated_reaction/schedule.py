__all__ = ["TemplatedSchedule", "TemplatedEmptySchedule", "TemplatedRepeatSchedule", "TemplatedListSchedule"]

from abc import abstractmethod
from dataclasses import dataclass

from ordered_set import OrderedSet

from ..templated_expressions import TemplatedExpression, ex_templated, free_variable_names
from ..templated_expressions.ast import BaseTemplatedFunction, TemplatedVariable


class TemplatedSchedule:
    """Base class for templated dose schedules."""

    @abstractmethod
    def get_schedule_variables(self) -> OrderedSet:
        pass


@dataclass(frozen=True, slots=True)
class TemplatedEmptySchedule(TemplatedSchedule):
    """A templated schedule with no dose times."""

    def get_schedule_variables(self) -> OrderedSet:
        return OrderedSet()


@dataclass(frozen=True, kw_only=True, slots=True)
class TemplatedRepeatSchedule(TemplatedSchedule):
    """A templated repeated schedule with interval, count, and optional amount or duration."""

    start: TemplatedExpression = ex_templated("0.0:Float64[dynamic]")
    interval: TemplatedExpression
    n: TemplatedExpression = ex_templated("inf:Float64[dynamic]")
    amount: TemplatedExpression | None = None
    duration: TemplatedExpression | None = None

    def get_schedule_variables(self) -> OrderedSet[TemplatedVariable | BaseTemplatedFunction]:
        start_variables = free_variable_names(self.start)
        interval_variables = free_variable_names(self.interval)
        n_variables = free_variable_names(self.n)
        if self.amount is not None:
            amount_variables = free_variable_names(self.amount)
        else:
            amount_variables = OrderedSet()
        if self.duration is not None:
            duration_variables = free_variable_names(self.duration)
        else:
            duration_variables = OrderedSet()
        return start_variables | interval_variables | n_variables | amount_variables | duration_variables


@dataclass(frozen=True, kw_only=True, slots=True)
class TemplatedListSchedule(TemplatedSchedule):
    """A templated schedule with explicit times and optional amounts or durations."""

    times: list[TemplatedExpression]
    amounts: list[TemplatedExpression] | None = None
    durations: list[TemplatedExpression] | None = None

    def get_schedule_variables(self) -> OrderedSet[TemplatedVariable | BaseTemplatedFunction]:
        times_variables = OrderedSet()
        amounts_variables = OrderedSet()
        durations_variables = OrderedSet()
        for time in self.times:
            times_variables |= free_variable_names(time)
        if self.amounts is not None:
            for amount in self.amounts:
                amounts_variables |= free_variable_names(amount)
        if self.durations is not None:
            for duration in self.durations:
                durations_variables |= free_variable_names(duration)

        return times_variables | amounts_variables | durations_variables
