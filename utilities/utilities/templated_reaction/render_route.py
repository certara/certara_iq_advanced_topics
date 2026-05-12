__all__ = [
    "make_new_effect",
    "make_new_schedule",
]

from functools import singledispatch

from ..reaction import DoseEffect, Effect, EmptySchedule, JumpEffect, ListSchedule, RepeatSchedule, Schedule
from ..templated_expressions import render, substitute
from ..templated_expressions.ast import BaseTemplatedFunction, TemplatedVariable
from ..templated_expressions.templated_name import TemplatedName
from .effect import TemplatedDoseEffect, TemplatedEffect, TemplatedJumpEffect
from .schedule import TemplatedEmptySchedule, TemplatedListSchedule, TemplatedRepeatSchedule, TemplatedSchedule


@singledispatch
def make_new_effect(
    effect: TemplatedEffect,
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> Effect:
    raise NotImplementedError(f"Effect type {type(effect)} not supported")


@make_new_effect.register(TemplatedDoseEffect)
def make_new_effect_dose(
    effect: TemplatedDoseEffect,
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> DoseEffect:
    updated_value = substitute(effect.value, template_map)
    new_value = render(updated_value, index_map)
    return DoseEffect(new_value)


@make_new_effect.register(TemplatedJumpEffect)
def make_new_effect_jump(
    effect: TemplatedJumpEffect,
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> JumpEffect:
    updated_value = substitute(effect.value, template_map)
    new_value = render(updated_value, index_map)
    return JumpEffect(new_value)


@singledispatch
def make_new_schedule(
    schedule: TemplatedSchedule,
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> Schedule:
    raise NotImplementedError(f"Schedule type {type(schedule)} not supported")


@make_new_schedule.register(TemplatedEmptySchedule)
def make_new_schedule_empty(
    schedule: TemplatedEmptySchedule,
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> EmptySchedule:
    return EmptySchedule()


@make_new_schedule.register(TemplatedListSchedule)
def make_new_schedule_list(
    schedule: TemplatedListSchedule,
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> ListSchedule:
    updated_times = [substitute(time, template_map) for time in schedule.times]
    new_times = [render(time, index_map) for time in updated_times]
    if schedule.amounts is not None:
        updated_amounts = [substitute(amount, template_map) for amount in schedule.amounts]
        new_amounts = [render(amount, index_map) for amount in updated_amounts]
    else:
        new_amounts = None
    if schedule.durations is not None:
        updated_durations = [substitute(duration, template_map) for duration in schedule.durations]
        new_durations = [render(duration, index_map) for duration in updated_durations]
    else:
        new_durations = None
    return ListSchedule(times=new_times, amounts=new_amounts, durations=new_durations)


@make_new_schedule.register(TemplatedRepeatSchedule)
def make_new_schedule_repeat(
    schedule: TemplatedRepeatSchedule,
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> RepeatSchedule:
    updated_start = substitute(schedule.start, template_map)
    new_start = render(updated_start, index_map)
    updated_interval = substitute(schedule.interval, template_map)
    new_interval = render(updated_interval, index_map)
    updated_n = substitute(schedule.n, template_map)
    new_n = render(updated_n, index_map)
    if schedule.amount is not None:
        updated_amount = substitute(schedule.amount, template_map)
        new_amount = render(updated_amount, index_map)
    else:
        new_amount = None
    if schedule.duration is not None:
        updated_duration = substitute(schedule.duration, template_map)
        new_duration = render(updated_duration, index_map)
    else:
        new_duration = None
    return RepeatSchedule(start=new_start, interval=new_interval, n=new_n, amount=new_amount, duration=new_duration)
