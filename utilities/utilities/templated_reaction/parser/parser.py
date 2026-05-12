__all__ = ["ReactionParsers"]

import math
import re
from dataclasses import replace
from typing import List, Tuple

from parsita import ParserContext, failure, lit, opt, pred, reg, rep, repsep, success
from parsita.util import constant, splat

from ...expressions.function_parser import ArgumentParserParameter, arguments
from ...helper import is_static, make_steady_state, or_else
from ...templated_expressions.ast import FloatLiteral, IntegerLiteral, TemplatedVariable
from ...templated_expressions.parser import TemplatedExpressionParsers, TemplatedVariableParser
from ...units import Unit
from ...units import ast as uast
from ...units.parser import UnitParsers
from .. import (
    TemplatedAssignment,
    TemplatedBindingOffReaction,
    TemplatedBindingOnReaction,
    TemplatedCompartment,
    TemplatedEmaxReaction,
    TemplatedForwardAnalyticReaction,
    TemplatedForwardMassActionReaction,
    TemplatedHalfLifeReaction,
    TemplatedMichaelisMentenReaction,
    TemplatedParameter,
    TemplatedReaction,
    TemplatedReactionModel,
    TemplatedReversibleAnalyticReaction,
    TemplatedReversibleMassActionReaction,
    TemplatedState,
    TemplatedSteadyStateReaction,
    TemplatedTransportReaction,
)
from ..effect import TemplatedDoseEffect, TemplatedJumpEffect
from ..event import TemplatedEvent
from ..initialization import (
    TemplatedInitialization,
    TemplatedInitialValue,
)
from ..route import TemplatedRoute
from ..schedule import TemplatedEmptySchedule, TemplatedListSchedule, TemplatedRepeatSchedule


def is_static_parameter(expression):
    if is_static(expression):
        return True

    match expression:
        case TemplatedVariable(name):
            if name.prefix != "" or len(name.interpolations) != 1:
                return False
            values = name.interpolations[0].variables
            if isinstance(values, str):
                return False
            return all(
                re.fullmatch(r"\d+((\.\d+([Ee][+-]?\d+)?)|((\.\d+)?[Ee][+-]?\d+))|\d+", value) for value in values
            )
        case _:
            return False


def make_model(
    initialization: TemplatedInitialization,
    time_unit: Unit,
    default_state_unit: Unit | None,
    global_names: List[Tuple[str, List[str]]] | None,
    components: List[
        Tuple[str, TemplatedParameter | TemplatedAssignment | TemplatedCompartment | TemplatedState | TemplatedRoute]
        | TemplatedReaction
        | TemplatedEvent
    ],
) -> TemplatedReactionModel:
    parameters = {}
    assignments = {}
    compartments = {}
    states = {}
    routes = {}
    reactions = []
    events = []

    globals = dict(global_names)

    component_names = set()

    for line in components:
        match line:
            case TemplatedReaction():
                reactions.append(line)
            case TemplatedEvent():
                events.append(line)
            case _:
                name, component = line
                match component:
                    case TemplatedParameter():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        parameters[name] = component

                    case TemplatedAssignment():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        assignments[name] = component

                    case TemplatedCompartment():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        compartments[name] = component

                    case TemplatedState():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        if component.unit is None:
                            states[name] = replace(component, unit=default_state_unit)
                        else:
                            states[name] = component

                    case TemplatedRoute():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        routes[name] = component

    return success(
        TemplatedReactionModel(
            globals=globals,
            parameters=parameters,
            assignments=assignments,
            states=states,
            compartments=compartments,
            routes=routes,
            events=events,
            reactions=reactions,
            initialization=initialization,
            time_unit=time_unit,
        )
    )


class ReactionParsers(ParserContext, whitespace=r"[ \t]*"):
    eol = reg(r"((#.*)?\n[ \t]*)*(#.*)?((\n[ \t]*)|\Z)")

    name = reg(r"[A-Za-z_][A-Za-z_0-9]*")
    number = reg(r"[+-]?\d+(\.\d+)?([Ee][+-]?\d+)?") > float
    integer = reg(r"\d+") > int
    global_variable = reg(r"[A-Za-z_0-9]+")

    template_characters = reg(r"[A-Za-z_0-9\[\]@,]*")
    one_template = "{" & template_characters & "}" > (lambda x: "".join(x))
    id_characters = opt(reg(r"[A-Za-z0-9_]*")) > (lambda x: x[0] or "")
    one_template_combo = one_template & id_characters > splat(lambda u, v: u + v)
    templated_part = rep(one_template_combo) > (lambda u: "".join(u))
    templated_name = TemplatedVariableParser.templated_name

    templated_expression = TemplatedExpressionParsers.expression
    expression_list = "[" >> repsep(templated_expression, ",") << "]"
    static_expression = pred(templated_expression, is_static, "static expression")
    static_parameter_expression = pred(templated_expression, is_static_parameter, "static parameter expression")

    unit = UnitParsers.unit
    unit_ascription = opt(":" >> unit) > or_else(None)

    # globals
    global_name = name & (lit("=") >> "[" >> repsep(global_variable, ",") << "]")

    # A parameter is name with unit colon-equals static value
    parameter = templated_name & (
        unit_ascription & ":=" >> static_parameter_expression > splat(lambda u, v: TemplatedParameter(v, u))
    )

    # An assignment is a name with unit equals definition
    assignment = templated_name & (
        unit_ascription & "=" >> templated_expression > splat(lambda u, d: TemplatedAssignment(d, u))
    )

    # A compartment is an name with unit equals size followed by the dimension
    dimension = lit("~") >> lit("0", "1", "2", "3") > int
    compartment = templated_name & (
        dimension & unit_ascription & "=" >> templated_expression > splat(lambda d, u, s: TemplatedCompartment(d, s, u))
    )

    # A state is a name star equals expression
    state_compartment = opt("@" >> templated_name) > or_else(None)
    state = templated_name & (
        state_compartment & unit_ascription & lit("*") >> lit("=") >> templated_expression
        > splat(lambda c, u, i: TemplatedState(i, c, u))
    )

    # A reaction is reactants then products then a few named parameters
    species_list = repsep(templated_name, "+")
    kf = lit("kf") >> "=" >> templated_expression
    kr = lit("kr") >> "=" >> templated_expression
    forward_mass_action_reaction = species_list << "->" & species_list & ";" >> kf > splat(
        TemplatedForwardMassActionReaction
    )
    reversible_mass_action_reaction = species_list << "<->" & species_list & ";" >> kf & "," >> kr > splat(
        TemplatedReversibleMassActionReaction
    )
    rf = lit("rf") >> "=" >> templated_expression
    rr = lit("rr") >> "=" >> templated_expression
    forward_analytic_reaction = species_list << "->" & species_list & ";" >> rf > splat(
        TemplatedForwardAnalyticReaction
    )
    reversible_analytic_reaction = species_list << "<->" & species_list & ";" >> rf & "," >> rr > splat(
        TemplatedReversibleAnalyticReaction
    )
    pdist = lit("pdist") >> "=" >> templated_expression
    tdist = lit("tdist") >> "=" >> templated_expression
    transport_reaction = species_list << "<->" & species_list & ";" >> pdist & "," >> tdist > splat(
        TemplatedTransportReaction
    )

    thalf = lit("thalf") >> "=" >> templated_expression
    half_life_first_order_reaction = species_list << "->" & species_list & ";" >> thalf > splat(
        TemplatedHalfLifeReaction
    )

    kd = lit("kd") >> "=" >> templated_expression
    kon = lit("kon") >> "=" >> templated_expression
    koff = lit("koff") >> "=" >> templated_expression
    binding_reaction_on = species_list << "<->" & species_list & ";" >> kd & "," >> kon > splat(
        TemplatedBindingOnReaction
    )
    binding_reaction_off = species_list << "<->" & species_list & ";" >> kd & "," >> koff > splat(
        TemplatedBindingOffReaction
    )

    emax = lit("emax") >> "=" >> templated_expression
    ec50 = lit("ec50") >> "=" >> templated_expression
    n = lit("n") >> "=" >> templated_expression
    emin = opt("," >> lit("emin") >> "=" >> templated_expression) > or_else(IntegerLiteral(0))
    emax_reaction = species_list << "->" & species_list & ";" >> emax & "," >> ec50 & "," >> n & emin > splat(
        TemplatedEmaxReaction
    )

    km = lit("km") >> "=" >> templated_expression
    kcat = lit("kcat") >> "=" >> templated_expression
    e = lit("e") >> "=" >> templated_expression
    michaelis_menten_reaction = species_list << "->" & species_list & ";" >> km & "," >> kcat & "," >> e > splat(
        TemplatedMichaelisMentenReaction
    )

    css = lit("css") >> "=" >> templated_expression
    thalf_ss = lit("thalf") >> "=" >> templated_expression
    v = opt("," >> lit("v") >> "=" >> templated_expression) > or_else(None)
    steady_state_reaction = species_list << "<->" & species_list & ";" >> css & "," >> thalf_ss & v > splat(
        TemplatedSteadyStateReaction
    )

    reaction = (
        forward_mass_action_reaction
        | reversible_mass_action_reaction
        | forward_analytic_reaction
        | reversible_analytic_reaction
        | transport_reaction
        | half_life_first_order_reaction
        | binding_reaction_on
        | binding_reaction_off
        | emax_reaction
        | michaelis_menten_reaction
        | steady_state_reaction
    )

    # A route is a name equals schedule followed by list of effects
    empty_schedule = lit("@") >> lit("(") >> lit(")") > constant(TemplatedEmptySchedule())

    list_schedule = (
        lit("@")
        >> "("
        >> arguments(
            keyword_only=[
                ArgumentParserParameter("times", expression_list),
                ArgumentParserParameter("amounts", expression_list, default=None),
                ArgumentParserParameter("durations", expression_list, default=None),
            ],
            keyword=name,
        )
        << ")"
    ) > (lambda args: TemplatedListSchedule(**args))

    repeat_schedule = (
        lit("@")
        >> "("
        >> arguments(
            keyword_only=[
                ArgumentParserParameter("start", templated_expression, default=FloatLiteral(0.0)),
                ArgumentParserParameter("interval", templated_expression),
                ArgumentParserParameter("n", templated_expression, default=FloatLiteral(math.inf)),
                ArgumentParserParameter("amount", templated_expression, default=None),
                ArgumentParserParameter("duration", templated_expression, default=None),
            ],
            keyword=name,
        )
        << ")"
    ) > (lambda args: TemplatedRepeatSchedule(**args))

    dose_effect = templated_name & lit("+=") >> "amt" >> "*" >> templated_expression > splat(
        lambda n, e: [n, TemplatedDoseEffect(e)]
    )
    dose_effect_1 = templated_name << lit("+=") << "amt" > (lambda n: [n, TemplatedDoseEffect(IntegerLiteral(1))])
    jump_effect = templated_name & lit("=") >> templated_expression > splat(lambda n, e: [n, TemplatedJumpEffect(e)])

    route = templated_name & (
        unit_ascription
        & "=" >> (empty_schedule | list_schedule | repeat_schedule)
        & ";" >> repsep(dose_effect | dose_effect_1 | jump_effect, ",")
        > splat(lambda u, s, e: TemplatedRoute(dict(e), s, u))
    )

    # Arbitrary events
    event_effect = templated_name & lit("=") >> templated_expression
    trigger = lit("@") >> "(" >> templated_expression << ")"
    event = trigger & ";" >> repsep(event_effect, ",") > splat(lambda t, e: TemplatedEvent(t, dict(e)))

    # Initialization
    initial_value = lit("initial_value") >> "(" >> ")" > constant(TemplatedInitialValue())
    time_scale = lit("time_scale") >> "=" >> static_expression
    max_time = lit("max_time") >> "=" >> static_expression
    steady_state_args = time_scale & opt(lit(",") >> max_time)
    steady_state = lit("steady_state") >> "(" >> steady_state_args << ")" > splat(make_steady_state)
    initialization = lit("initialization") >> "=" >> (initial_value | steady_state) << eol

    # Model
    header = lit("%%") >> "ReactionModel@2" >> eol

    components = rep(
        (parameter << eol)
        | (assignment << eol)
        | (compartment << eol)
        | (state << eol)
        | (route << eol)
        | (reaction << eol)
        | (event << eol)
    )

    globals_section = opt(lit("%") >> "template_globals" >> eol >> rep(global_name << eol)) > or_else([])
    components_section = lit("%") >> "components" >> eol >> components

    header_section = header >> arguments(
        keyword_only=[
            ArgumentParserParameter("initialization", (initial_value | steady_state), default=TemplatedInitialValue()),
            ArgumentParserParameter("time_unit", unit, default=uast.Dimensionless()),
            ArgumentParserParameter("default_state_unit", unit, default=None),
        ],
        keyword=name,
        separator=eol,
    )

    unsafe_model = (opt(eol) >> header_section & globals_section & components_section) >= splat(
        lambda h, g, c: make_model(
            initialization=h["initialization"],
            time_unit=h["time_unit"],
            default_state_unit=h["default_state_unit"],
            global_names=g,
            components=c,
        )
    )
