__all__ = ["TemplatedRoute"]

from dataclasses import dataclass

from ..units import Unit
from .effect import TemplatedEffect
from .schedule import TemplatedSchedule


@dataclass(frozen=True, slots=True)
class TemplatedRoute:
    """A templated dosing route with schedule, effects, and optional amount units."""

    effects: dict[str, TemplatedEffect]
    schedule: TemplatedSchedule
    amount_unit: Unit | None = None  # None here means infer from the schedule
