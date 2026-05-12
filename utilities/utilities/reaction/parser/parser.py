__all__ = ["ReactionParsers"]

import math
from dataclasses import replace
from typing import List, Tuple

from parsita import ParserContext, failure, lit, opt, pred, reg, rep, repsep, success
from parsita.util import constant, splat

from ...expressions.ast import Ascription, FloatLiteral, IntegerLiteral
from ...expressions.function_parser import ArgumentParserParameter, arguments
from ...expressions.parser import ExpressionParsers
from ...helper import is_static, make_reaction_steady_state, or_else
from ...types import ast as tast
from ...units import Unit
from ...units import ast as uast
from ...units.parser import UnitParsers
from .. import (
    BindingOffReaction,
    BindingOnReaction,
    EmaxReaction,
    ForwardAnalyticReaction,
    ForwardMassActionReaction,
    HalfLifeReaction,
    MichaelisMentenReaction,
    Reaction,
    ReversibleAnalyticReaction,
    ReversibleMassActionReaction,
    SteadyStateReaction,
    TransportReaction,
)
from ..effect import DoseEffect, JumpEffect
from ..event import Event
from ..initialization import (
    Initialization,
    InitialValue,
)
from ..model import (
    Assignment,
    Compartment,
    Parameter,
    ReactionModel,
    State,
)
from ..route import Route
from ..schedule import EmptySchedule, ListSchedule, RepeatSchedule


def make_model(
    initialization: Initialization,
    time_unit: Unit,
    default_state_unit: Unit | None,
    components: List[Tuple[str, Parameter | Assignment | Compartment | State | Route] | Reaction | Event],
) -> ReactionModel:
    parameters = {}
    assignments = {}
    compartments = {}
    states = {}
    routes = {}
    reactions = []
    events = []

    component_names = set()

    for line in components:
        match line:
            case Reaction():
                reactions.append(line)
            case Event():
                events.append(line)
            case _:
                name, component = line
                match component:
                    case Parameter():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        parameters[name] = component

                    case Assignment():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        assignments[name] = component

                    case Compartment():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        compartments[name] = component

                    case State():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        if component.unit is None:
                            states[name] = replace(component, unit=default_state_unit)
                        else:
                            states[name] = component

                    case Route():
                        if name in component_names:
                            return failure(f"component '{name}' to appear once")

                        component_names.add(name)
                        routes[name] = component

    return success(
        ReactionModel(
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
    # Reuse primitives
    eol = reg(r"((#.*)?\n[ \t]*)*(#.*)?((\n[ \t]*)|\Z)")

    name = reg(r"[A-Za-z_][A-Za-z_0-9]*")
    number = reg(r"[+-]?\d+(\.\d+)?([Ee][+-]?\d+)?") > float
    integer = reg(r"\d+") > int

    expression = ExpressionParsers.expression
    expression_list = "[" >> repsep(expression, ",") << "]"
    static_expression = pred(expression, is_static, "static expression")

    unit = UnitParsers.unit
    unit_ascription = opt(":" >> unit) > or_else(None)

    # A parameter is name with unit colon-equals static value
    parameter = name & (unit_ascription & ":=" >> static_expression > splat(lambda u, v: Parameter(v, u)))

    # An assignment is a name with unit equals definition
    assignment = name & (unit_ascription & "=" >> expression > splat(lambda u, d: Assignment(d, u)))

    # A compartment is an name with unit equals size followed by the dimension
    dimension = lit("~") >> lit("0", "1", "2", "3") > int
    compartment = name & (dimension & unit_ascription & "=" >> expression > splat(lambda d, u, s: Compartment(d, s, u)))

    # A state is a name star equals expression
    state_compartment = opt("@" >> name) > or_else(None)
    state = name & (
        state_compartment & unit_ascription & lit("*") >> lit("=") >> expression > splat(lambda c, u, i: State(i, c, u))
    )

    # A reaction is reactants then products then a few named parameters
    species_list = repsep(name, "+")
    kf = lit("kf") >> "=" >> expression
    kr = lit("kr") >> "=" >> expression
    forward_mass_action_reaction = species_list << "->" & species_list & ";" >> kf > splat(ForwardMassActionReaction)
    reversible_mass_action_reaction = species_list << "<->" & species_list & ";" >> kf & "," >> kr > splat(
        ReversibleMassActionReaction
    )
    rf = lit("rf") >> "=" >> expression
    rr = lit("rr") >> "=" >> expression
    forward_analytic_reaction = species_list << "->" & species_list & ";" >> rf > splat(ForwardAnalyticReaction)
    reversible_analytic_reaction = species_list << "<->" & species_list & ";" >> rf & "," >> rr > splat(
        ReversibleAnalyticReaction
    )
    pdist = lit("pdist") >> "=" >> expression
    tdist = lit("tdist") >> "=" >> expression
    transport_reaction = species_list << "<->" & species_list & ";" >> pdist & "," >> tdist > splat(TransportReaction)

    thalf = lit("thalf") >> "=" >> expression
    half_life_first_order_reaction = species_list << "->" & species_list & ";" >> thalf > splat(HalfLifeReaction)

    kd = lit("kd") >> "=" >> expression
    kon = lit("kon") >> "=" >> expression
    koff = lit("koff") >> "=" >> expression
    binding_reaction_on = species_list << "<->" & species_list & ";" >> kd & "," >> kon > splat(BindingOnReaction)
    binding_reaction_off = species_list << "<->" & species_list & ";" >> kd & "," >> koff > splat(BindingOffReaction)

    emax = lit("emax") >> "=" >> expression
    ec50 = lit("ec50") >> "=" >> expression
    n = lit("n") >> "=" >> expression
    emin = opt("," >> lit("emin") >> "=" >> expression) > or_else(
        Ascription(IntegerLiteral(0), tast.Float64(uast.Dynamic()))
    )
    emax_reaction = species_list << "->" & species_list & ";" >> emax & "," >> ec50 & "," >> n & emin > splat(
        EmaxReaction
    )

    km = lit("km") >> "=" >> expression
    kcat = lit("kcat") >> "=" >> expression
    e = lit("e") >> "=" >> expression
    michaelis_menten_reaction = species_list << "->" & species_list & ";" >> km & "," >> kcat & "," >> e > splat(
        MichaelisMentenReaction
    )

    css = lit("css") >> "=" >> expression
    thalf_ss = lit("thalf") >> "=" >> expression
    v = opt("," >> lit("v") >> "=" >> expression) > or_else(None)
    steady_state_reaction = species_list << "<->" & species_list & ";" >> css & "," >> thalf_ss & v > splat(
        SteadyStateReaction
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
    empty_schedule = lit("@") >> lit("(") >> lit(")") > constant(EmptySchedule())

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
    ) > (lambda args: ListSchedule(**args))

    repeat_schedule = (
        lit("@")
        >> "("
        >> arguments(
            keyword_only=[
                ArgumentParserParameter(
                    "start", expression, default=Ascription(FloatLiteral(0.0), tast.Float64(uast.Dynamic()))
                ),
                ArgumentParserParameter("interval", expression),
                ArgumentParserParameter(
                    "n", expression, default=Ascription(FloatLiteral(math.inf), tast.Float64(uast.Dynamic()))
                ),
                ArgumentParserParameter("amount", expression, default=None),
                ArgumentParserParameter("duration", expression, default=None),
            ],
            keyword=name,
        )
        << ")"
    ) > (lambda args: RepeatSchedule(**args))

    dose_effect = name & lit("+=") >> "amt" >> "*" >> expression > splat(lambda n, e: [n, DoseEffect(e)])
    dose_effect_1 = name << lit("+=") << "amt" > (lambda n: [n, DoseEffect(IntegerLiteral(1))])
    jump_effect = name & lit("=") >> expression > splat(lambda n, e: [n, JumpEffect(e)])

    route = name & (
        unit_ascription
        & "=" >> (empty_schedule | list_schedule | repeat_schedule)
        & ";" >> repsep(dose_effect | dose_effect_1 | jump_effect, ",")
        > splat(lambda u, s, e: Route(dict(e), s, u))
    )

    # Arbitrary events
    event_effect = name & lit("=") >> expression
    trigger = lit("@") >> "(" >> expression << ")"
    event = trigger & ";" >> repsep(event_effect, ",") > splat(lambda t, e: Event(t, dict(e)))

    # Initialization
    initial_value = lit("initial_value") >> "(" >> ")" > constant(InitialValue())
    time_scale = lit("time_scale") >> "=" >> static_expression
    max_time = lit("max_time") >> "=" >> static_expression
    steady_state_args = time_scale & opt(lit(",") >> max_time)
    steady_state = lit("steady_state") >> "(" >> steady_state_args << ")" > splat(make_reaction_steady_state)
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
    components_section = lit("%") >> "components" >> eol >> components

    header_section = header >> arguments(
        keyword_only=[
            ArgumentParserParameter("initialization", (initial_value | steady_state), default=InitialValue()),
            ArgumentParserParameter("time_unit", unit, default=uast.Dimensionless()),
            ArgumentParserParameter("default_state_unit", unit, default=None),
        ],
        keyword=name,
        separator=eol,
    )

    unsafe_model = (opt(eol) >> header_section & components_section) >= splat(
        lambda h, c: make_model(
            initialization=h["initialization"],
            time_unit=h["time_unit"],
            default_state_unit=h["default_state_unit"],
            components=c,
        )
    )
