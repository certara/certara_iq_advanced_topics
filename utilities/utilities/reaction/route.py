__all__ = ["Route"]

from dataclasses import dataclass

from ..units import Unit
from ..units.deparser import deparse_unit
from .effect import Effect
from .schedule import Schedule


@dataclass(frozen=True, slots=True)
class Route:
    """A concrete dosing route with schedule, effects, and optional amount units."""

    effects: dict[str, Effect]
    schedule: Schedule
    amount_unit: Unit | None = None  # None here means infer from the schedule

    def deparse(self, name: str) -> str:
        effect_strs = ", ".join(effect.deparse(effect_name) for effect_name, effect in self.effects.items())
        schedule_str = self.schedule.deparse()
        if self.amount_unit is not None:
            return f"{name}:{deparse_unit(self.amount_unit)} = {schedule_str}; {effect_strs}"
        else:
            return f"{name} = {schedule_str}; {effect_strs}"
