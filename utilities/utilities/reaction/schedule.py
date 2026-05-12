__all__ = ["Schedule", "EmptySchedule", "RepeatSchedule", "ListSchedule"]

from abc import abstractmethod
from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression
from ..expressions.parser import ex


class Schedule:
    """Base class for concrete dose schedules."""

    @abstractmethod
    def deparse(self) -> str:
        pass


@dataclass(frozen=True, slots=True)
class EmptySchedule(Schedule):
    """A schedule with no dose times."""

    def deparse(self) -> str:
        return "@()"


@dataclass(frozen=True, kw_only=True, slots=True)
class RepeatSchedule(Schedule):
    """A repeated schedule with interval, count, and optional amount or duration."""

    start: Expression = ex("0.0")
    interval: Expression
    n: Expression = ex("inf")
    amount: Expression | None = None
    duration: Expression | None = None

    def deparse(self) -> str:
        if self.amount is not None:
            if self.duration is not None:
                return (
                    f"@(start={deparse_expression(self.start)}, interval={deparse_expression(self.interval)}, "
                    f"n={deparse_expression(self.n)}, amount={deparse_expression(self.amount)}, "
                    f"duration={deparse_expression(self.duration)})"
                )
            else:
                return (
                    f"@(start={deparse_expression(self.start)}, interval={deparse_expression(self.interval)}, "
                    f"n={deparse_expression(self.n)}, amount={deparse_expression(self.amount)})"
                )
        return (
            f"@(start={deparse_expression(self.start)}, interval={deparse_expression(self.interval)}, "
            f"n={deparse_expression(self.n)})"
        )


@dataclass(frozen=True, kw_only=True, slots=True)
class ListSchedule(Schedule):
    """A schedule with explicit times and optional amounts or durations."""

    times: list[Expression]
    amounts: list[Expression] | None = None
    durations: list[Expression] | None = None

    def deparse(self) -> str:
        if self.amounts is not None:
            if self.durations is not None:
                return (
                    f"@(times=[{', '.join(deparse_expression(t) for t in self.times)}], "
                    f"amounts=[{', '.join(deparse_expression(a) for a in self.amounts)}], "
                    f"durations=[{', '.join(deparse_expression(d) for d in self.durations)}])"
                )
            else:
                return (
                    f"@(times=[{', '.join(deparse_expression(t) for t in self.times)}], "
                    f"amounts=[{', '.join(deparse_expression(a) for a in self.amounts)}])"
                )
        return f"@(times=[{', '.join(deparse_expression(t) for t in self.times)}])"
