from __future__ import annotations

from ordered_set import OrderedSet

__all__ = ["TemplatedReactionModel"]

from dataclasses import dataclass
from pathlib import Path

from parsita import Failure, Result, Success

from ..reaction import Assignment, Compartment, Event, InitialValue, Parameter, ReactionModel, Route, State, SteadyState
from ..templated_expressions import free_variable_names, render, substitute
from ..templated_expressions.templated_name import TemplatedName
from ..units import Unit
from ..units import ast as uast
from .assignment import TemplatedAssignment
from .base import TemplatedReaction
from .compartment import TemplatedCompartment
from .event import TemplatedEvent
from .initialization import TemplatedInitialization, TemplatedInitialValue
from .parameter import TemplatedParameter
from .render_route import (
    make_new_effect,
    make_new_schedule,
)
from .route import TemplatedRoute
from .state import TemplatedState


@dataclass(frozen=True, slots=True)
class TemplatedReactionModel:
    """A parsed templated ReactionModel that can be expanded into concrete model text.

    Template globals define string arrays used by ``{...}`` interpolations in
    component names and expressions. Rendering expands those templates into a
    regular ReactionModel with no templating syntax remaining.
    """

    globals: dict[str, list[str]]
    parameters: dict[TemplatedName, TemplatedParameter]
    assignments: dict[TemplatedName, TemplatedAssignment]
    compartments: dict[TemplatedName, TemplatedCompartment]
    states: dict[TemplatedName, TemplatedState]
    reactions: list[TemplatedReaction]
    routes: dict[TemplatedName, TemplatedRoute]
    events: list[TemplatedEvent]
    initialization: TemplatedInitialization = TemplatedInitialValue()
    time_unit: Unit = uast.Dimensionless()

    @staticmethod
    def from_text(text: str) -> TemplatedReactionModel:
        """Parse templated ReactionModel text into a ``TemplatedReactionModel``.

        The input should include the standard ``%% ReactionModel@2`` header and
        may include an optional ``% template_globals`` section before components.
        """

        from .parser import ReactionParsers

        result: Result[TemplatedReactionModel] = ReactionParsers.unsafe_model.parse(text)
        match result:
            case Failure(error):
                return str(error)
            case Success(unsafe_model):
                return unsafe_model

    @staticmethod
    def from_file(path: str | Path) -> TemplatedReactionModel:
        """Read UTF-8 templated ReactionModel text from ``path`` and parse it."""

        if isinstance(path, str):
            path = Path(path)

        return TemplatedReactionModel.from_text(path.read_text(encoding="utf-8"))

    def _to_reaction_model(self) -> ReactionModel:
        """Render this template into an in-memory concrete ``ReactionModel``."""

        from .render_reaction import render_reaction
        from .render_template.generate_index_maps import generate_index_maps
        from .render_template.validate_templates import validate_and_update_templates

        # handle parameters
        parameters = {}
        for parameter_name, parameter_expression in self.parameters.items():
            template_map, label_index_map = validate_and_update_templates(parameter_name, self.globals)
            parameter_templated_name = template_map[parameter_name]
            combinations = generate_index_maps(label_index_map)
            for combination in combinations:
                new_parameter_name = parameter_templated_name.render(combination)
                if new_parameter_name in parameters:
                    raise ValueError(
                        f"Parameter name {new_parameter_name} is already defined. "
                        f"Check your template for {parameter_name}"
                    )
                parameters[new_parameter_name] = Parameter(
                    render(parameter_expression.value, combination), parameter_expression.unit
                )

        # handle assignments
        assignments = {}
        for assignment_name, assignment in self.assignments.items():
            # get the assignment variables
            variable_names = free_variable_names(assignment.definition)
            # name and all variables
            all_names = [assignment_name, *variable_names]
            # validation and replace globals
            template_map, label_index_map = validate_and_update_templates(all_names, self.globals)
            updated_assignment_definition = substitute(assignment.definition, template_map)
            combinations = generate_index_maps(label_index_map)
            for combination in combinations:
                new_assignment_name = template_map[assignment_name].render(combination)
                if new_assignment_name in assignments:
                    raise ValueError(
                        f"Assignment name {new_assignment_name} is already defined. "
                        f"Check your template for {assignment_name}"
                    )
                new_assignment_definition = render(updated_assignment_definition, combination)
                assignments[new_assignment_name] = Assignment(
                    definition=new_assignment_definition, unit=assignment.unit
                )

        # handle compartments
        compartments = {}
        for compartment_name, compartment in self.compartments.items():
            variable_names = free_variable_names(compartment.size)
            all_names = [compartment_name, *variable_names]
            template_map, label_index_map = validate_and_update_templates(all_names, self.globals)
            updated_compartment_size = substitute(compartment.size, template_map)
            combinations = generate_index_maps(label_index_map)
            for combination in combinations:
                new_compartment_name = template_map[compartment_name].render(combination)
                if new_compartment_name in compartments:
                    raise ValueError(
                        f"Compartment name {new_compartment_name} is already defined. "
                        f"Check your template for {compartment_name}"
                    )
                new_compartment_size = render(updated_compartment_size, combination)
                compartments[new_compartment_name] = Compartment(
                    dimension=compartment.dimension, size=new_compartment_size, unit=compartment.unit
                )

        # handle states
        states = {}
        for state_name, state in self.states.items():
            variable_names = free_variable_names(state.initial_value)
            if state.compartment is not None:
                all_names = [state_name, state.compartment, *variable_names]
            else:
                all_names = [state_name, *variable_names]
            template_map, label_index_map = validate_and_update_templates(all_names, self.globals)
            updated_state_initial_value = substitute(state.initial_value, template_map)
            combinations = generate_index_maps(label_index_map)
            for combination in combinations:
                new_state_name = template_map[state_name].render(combination)
                if new_state_name in states:
                    raise ValueError(
                        f"State name {new_state_name} is already defined. Check your template for {state_name}"
                    )
                if state.compartment is not None:
                    new_compartment_name = template_map[state.compartment].render(combination)
                else:
                    new_compartment_name = None
                new_initial_value = render(updated_state_initial_value, combination)
                states[new_state_name] = State(
                    initial_value=new_initial_value, compartment=new_compartment_name, unit=state.unit
                )

        # handle reactions
        reactions = []
        for reaction in self.reactions:
            reactions.extend(render_reaction(reaction, self.globals))

        # handle routes
        routes = {}
        for route_name, route in self.routes.items():
            effect_names = []
            effect_variable_names = []
            for effect_name, effect in route.effects.items():
                effect_names.append(effect_name)
                effect_variable_names.extend(effect.get_effect_variables())
            schedule_variable_names = route.schedule.get_schedule_variables()
            all_names = [
                route_name,
                *effect_names,
                *effect_variable_names,
                *schedule_variable_names,
            ]
            template_map, label_index_map = validate_and_update_templates(all_names, self.globals)
            combinations = generate_index_maps(label_index_map)
            for combination in combinations:
                new_route_name = template_map[route_name].render(combination)
                if new_route_name in routes:
                    raise ValueError(
                        f"Route name {new_route_name} is already defined. Check your template for {route_name}"
                    )
                new_effects = {}
                for effect_name, effect in route.effects.items():
                    new_effect_name = template_map[effect_name].render(combination)
                    new_effect = make_new_effect(effect, template_map, combination)
                    new_effects[new_effect_name] = new_effect
                new_schedule = make_new_schedule(route.schedule, template_map, combination)
                routes[new_route_name] = Route(
                    effects=new_effects,
                    schedule=new_schedule,
                    amount_unit=route.amount_unit,
                )

        # handle events
        events = []
        for event in self.events:
            trigger_variable_names = free_variable_names(event.trigger)
            effect_names = []
            effect_variable_names = []
            for name_i, effect_i in event.effects.items():
                effect_names.append(name_i)
                effect_variables_i = free_variable_names(effect_i)
                effect_variable_names.extend(effect_variables_i)
            all_names = [
                *effect_names,
                *trigger_variable_names,
                *effect_variable_names,
            ]
            template_map, label_index_map = validate_and_update_templates(all_names, self.globals)

            all_combinations = generate_index_maps(label_index_map)
            for combination in all_combinations:
                new_effects = {}
                updated_trigger = substitute(event.trigger, template_map)
                new_trigger = render(updated_trigger, combination)
                for effect_name, effect in event.effects.items():
                    new_effect_name = template_map[effect_name].render(combination)
                    updated_effect = substitute(effect, template_map)
                    new_effect = render(updated_effect, combination)
                    new_effects[new_effect_name] = new_effect
                events.append(Event(trigger=new_trigger, effects=new_effects))

        if isinstance(self.initialization, TemplatedInitialValue):
            initialization = InitialValue()
        else:
            time_scale = render(self.initialization.time_scale, {})
            if self.initialization.max_time is not None:
                max_time = render(self.initialization.max_time, {})
                initialization = SteadyState(time_scale=time_scale, max_time=max_time)
            else:
                initialization = SteadyState(time_scale=time_scale)

        return ReactionModel(
            parameters=parameters,
            assignments=assignments,
            compartments=compartments,
            states=states,
            reactions=reactions,
            routes=routes,
            events=events,
            initialization=initialization,
            time_unit=self.time_unit,
        )

    def to_reaction_model(self, path: str | Path) -> None:
        """Render the template and write concrete ReactionModel text to ``path``."""

        path = Path(path)
        reaction_model = self._to_reaction_model()
        reaction_model.to_text(path)
