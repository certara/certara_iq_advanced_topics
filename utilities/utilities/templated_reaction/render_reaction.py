from functools import singledispatch

from ordered_set import OrderedSet

from ..reaction import (
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
from ..templated_expressions import free_variable_names, render, substitute
from ..templated_expressions.ast import BaseTemplatedFunction, TemplatedVariable
from ..templated_expressions.templated_name import TemplatedName
from .analytic import (
    TemplatedForwardAnalyticReaction,
    TemplatedReversibleAnalyticReaction,
)
from .base import TemplatedReaction
from .binding import TemplatedBindingOffReaction, TemplatedBindingOnReaction
from .emax import TemplatedEmaxReaction
from .half_life import TemplatedHalfLifeReaction
from .mass_action import (
    TemplatedForwardMassActionReaction,
    TemplatedReversibleMassActionReaction,
)
from .michaelis_menten import TemplatedMichaelisMentenReaction
from .render_template.generate_index_maps import generate_index_maps
from .render_template.validate_templates import validate_and_update_templates
from .steady_state import TemplatedSteadyStateReaction
from .transport import TemplatedTransportReaction


def render_reaction(reaction: TemplatedReaction, globals: dict[str, list[str]]) -> Reaction:
    variables_names = get_variables(reaction)
    all_names = [*reaction.reactants, *reaction.products, *variables_names]
    template_map, label_index_map = validate_and_update_templates(all_names, globals)
    all_combinations = generate_index_maps(label_index_map)
    updated_reactions = []
    for combination in all_combinations:
        new_reactants = [template_map[reactant].render(combination) for reactant in reaction.reactants]
        new_products = [template_map[product].render(combination) for product in reaction.products]

        new_reaction = make_new_reaction(reaction, new_reactants, new_products, template_map, combination)
        updated_reactions.append(new_reaction)
    return updated_reactions


@singledispatch
def get_variables(self: Reaction) -> OrderedSet[str]:
    raise NotImplementedError(f"get_variables not implemented for type {type(self).__name__}")


@get_variables.register(TemplatedForwardMassActionReaction)
def get_variables_forward_mass_action(self: TemplatedForwardAnalyticReaction) -> OrderedSet[str]:
    return free_variable_names(self.parameter)


@get_variables.register(TemplatedReversibleMassActionReaction)
def get_variables_reversible_mass_action(self: TemplatedReversibleMassActionReaction) -> OrderedSet[str]:
    return free_variable_names(self.forward_parameter) | free_variable_names(self.reverse_parameter)


@get_variables.register(TemplatedForwardAnalyticReaction)
def get_variables_forward_analytic(self: TemplatedForwardAnalyticReaction) -> OrderedSet[str]:
    return free_variable_names(self.rate)


@get_variables.register(TemplatedReversibleAnalyticReaction)
def get_variables_reversible_analytic(self: TemplatedReversibleAnalyticReaction) -> OrderedSet[str]:
    return free_variable_names(self.forward_rate) | free_variable_names(self.reverse_rate)


@get_variables.register(TemplatedBindingOnReaction)
def get_variables_binding_on(self: TemplatedBindingOnReaction) -> OrderedSet[str]:
    return free_variable_names(self.dissociation_parameter) | free_variable_names(self.association_rate_parameter)


@get_variables.register(TemplatedBindingOffReaction)
def get_variables_binding_off(self: TemplatedBindingOffReaction) -> OrderedSet[str]:
    return free_variable_names(self.dissociation_parameter) | free_variable_names(self.dissociation_rate_parameter)


@get_variables.register(TemplatedEmaxReaction)
def get_variables_emax(self: TemplatedEmaxReaction) -> OrderedSet[str]:
    return (
        free_variable_names(self.maximum_rate)
        | free_variable_names(self.half_maximal_effect_concentration)
        | free_variable_names(self.hill_coefficient)
        | free_variable_names(self.minimum_rate)
    )


@get_variables.register(TemplatedHalfLifeReaction)
def get_variables_half_life(self: TemplatedHalfLifeReaction) -> OrderedSet[str]:
    return free_variable_names(self.half_life)


@get_variables.register(TemplatedMichaelisMentenReaction)
def get_variables_michaelis_menten(self: TemplatedMichaelisMentenReaction) -> OrderedSet[str]:
    return (
        free_variable_names(self.km)
        | free_variable_names(self.michaelis_parameter)
        | free_variable_names(self.catalytic_rate_parameter)
        | free_variable_names(self.enzyme_amount)
    )


@get_variables.register(TemplatedTransportReaction)
def get_variables_transport(self: TemplatedTransportReaction) -> OrderedSet[str]:
    return free_variable_names(self.partition_coefficient) | free_variable_names(self.distribution_half_life)


@get_variables.register(TemplatedSteadyStateReaction)
def get_variables_steady_state(self: TemplatedSteadyStateReaction) -> OrderedSet[str]:
    return (
        free_variable_names(self.steady_state_concentration)
        | free_variable_names(self.half_life)
        | (free_variable_names(self.volume) if self.volume is not None else OrderedSet())
    )


@singledispatch
def make_new_reaction(
    self: TemplatedReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> Reaction:
    raise NotImplementedError(f"make new reaction is not implemented for type {type(self).__name__}")


@make_new_reaction.register(TemplatedForwardMassActionReaction)
def make_new_reaction_forward_mass_action(
    self: TemplatedForwardMassActionReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> ForwardMassActionReaction:
    updated_parameter = substitute(self.parameter, template_map)
    new_parameter = render(updated_parameter, index_map)
    return ForwardMassActionReaction(reactants=new_reactants, products=new_products, parameter=new_parameter)


@make_new_reaction.register(TemplatedReversibleMassActionReaction)
def make_new_reaction_reversible_mass_action(
    self: TemplatedReversibleMassActionReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> ReversibleMassActionReaction:
    updated_forward_parameter = substitute(self.forward_parameter, template_map)
    updated_reverse_parameter = substitute(self.reverse_parameter, template_map)
    new_forward_parameter = render(updated_forward_parameter, index_map)
    new_reverse_parameter = render(updated_reverse_parameter, index_map)
    return ReversibleMassActionReaction(
        reactants=new_reactants,
        products=new_products,
        forward_parameter=new_forward_parameter,
        reverse_parameter=new_reverse_parameter,
    )


@make_new_reaction.register(TemplatedForwardAnalyticReaction)
def make_new_reaction_forward_analytic(
    self: TemplatedForwardAnalyticReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> ForwardAnalyticReaction:
    updated_rate = substitute(self.rate, template_map)
    new_rate = render(updated_rate, index_map)
    return ForwardAnalyticReaction(reactants=new_reactants, products=new_products, rate=new_rate)


@make_new_reaction.register(TemplatedReversibleAnalyticReaction)
def make_new_reaction_reversible_analytic(
    self: TemplatedReversibleAnalyticReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> ReversibleAnalyticReaction:
    updated_forward_rate = substitute(self.forward_rate, template_map)
    updated_reverse_rate = substitute(self.reverse_rate, template_map)
    new_forward_rate = render(updated_forward_rate, index_map)
    new_reverse_rate = render(updated_reverse_rate, index_map)
    return ReversibleAnalyticReaction(
        reactants=new_reactants,
        products=new_products,
        forward_rate=new_forward_rate,
        reverse_rate=new_reverse_rate,
    )


@make_new_reaction.register(TemplatedBindingOnReaction)
def make_new_reaction_binding_on(
    self: TemplatedBindingOnReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> BindingOnReaction:
    updated_dissociation_parameter = substitute(self.dissociation_parameter, template_map)
    updated_association_rate_parameter = substitute(self.association_rate_parameter, template_map)
    new_dissociation_parameter = render(updated_dissociation_parameter, index_map)
    new_association_rate_parameter = render(updated_association_rate_parameter, index_map)
    return BindingOnReaction(
        reactants=new_reactants,
        products=new_products,
        dissociation_parameter=new_dissociation_parameter,
        association_rate_parameter=new_association_rate_parameter,
    )


@make_new_reaction.register(TemplatedBindingOffReaction)
def make_new_reaction_binding_off(
    self: TemplatedBindingOffReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> BindingOffReaction:
    updated_dissociation_parameter = substitute(self.dissociation_parameter, template_map)
    updated_dissociation_rate_parameter = substitute(self.dissociation_rate_parameter, template_map)
    new_dissociation_parameter = render(updated_dissociation_parameter, index_map)
    new_dissociation_rate_parameter = render(updated_dissociation_rate_parameter, index_map)
    return BindingOffReaction(
        reactants=new_reactants,
        products=new_products,
        dissociation_parameter=new_dissociation_parameter,
        dissociation_rate_parameter=new_dissociation_rate_parameter,
    )


@make_new_reaction.register(TemplatedEmaxReaction)
def make_new_reaction_emax(
    self: TemplatedEmaxReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> EmaxReaction:
    updated_maximum_rate = substitute(self.maximum_rate, template_map)
    updated_half_maximal_effect_concentration = substitute(self.half_maximal_effect_concentration, template_map)
    updated_hill_coefficient = substitute(self.hill_coefficient, template_map)
    updated_minimum_rate = substitute(self.minimum_rate, template_map)
    new_maximum_rate = render(updated_maximum_rate, index_map)
    new_half_maximal_effect_concentration = render(updated_half_maximal_effect_concentration, index_map)
    new_hill_coefficient = render(updated_hill_coefficient, index_map)
    new_minimum_rate = render(updated_minimum_rate, index_map)
    return EmaxReaction(
        reactants=new_reactants,
        products=new_products,
        maximum_rate=new_maximum_rate,
        half_maximal_effect_concentration=new_half_maximal_effect_concentration,
        hill_coefficient=new_hill_coefficient,
        minimum_rate=new_minimum_rate,
    )


@make_new_reaction.register(TemplatedHalfLifeReaction)
def make_new_reaction_half_life(
    self: TemplatedHalfLifeReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> HalfLifeReaction:
    updated_half_life = substitute(self.half_life, template_map)
    new_half_life = render(updated_half_life, index_map)
    return HalfLifeReaction(reactants=new_reactants, products=new_products, half_life=new_half_life)


@make_new_reaction.register(TemplatedMichaelisMentenReaction)
def make_new_reaction_michaelis_menten(
    self: TemplatedMichaelisMentenReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> MichaelisMentenReaction:
    updated_km = substitute(self.km, template_map)
    updated_michaelis_parameter = substitute(self.michaelis_parameter, template_map)
    updated_catalytic_rate_parameter = substitute(self.catalytic_rate_parameter, template_map)
    updated_enzyme_amount = substitute(self.enzyme_amount, template_map)
    new_km = render(updated_km, index_map)
    new_michaelis_parameter = render(updated_michaelis_parameter, index_map)
    new_catalytic_rate_parameter = render(updated_catalytic_rate_parameter, index_map)
    new_enzyme_amount = render(updated_enzyme_amount, index_map)
    return MichaelisMentenReaction(
        reactants=new_reactants,
        products=new_products,
        km=new_km,
        michaelis_parameter=new_michaelis_parameter,
        catalytic_rate_parameter=new_catalytic_rate_parameter,
        enzyme_amount=new_enzyme_amount,
    )


@make_new_reaction.register(TemplatedTransportReaction)
def make_new_reaction_transport(
    self: TemplatedTransportReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> TransportReaction:
    updated_partition_coefficient = substitute(self.partition_coefficient, template_map)
    updated_distribution_half_life = substitute(self.distribution_half_life, template_map)
    new_partition_coefficient = render(updated_partition_coefficient, index_map)
    new_distribution_half_life = render(updated_distribution_half_life, index_map)
    return TransportReaction(
        reactants=new_reactants,
        products=new_products,
        partition_coefficient=new_partition_coefficient,
        distribution_half_life=new_distribution_half_life,
    )


@make_new_reaction.register(TemplatedSteadyStateReaction)
def make_new_reaction_steady_state(
    self: TemplatedSteadyStateReaction,
    new_reactants: list[str],
    new_products: list[str],
    template_map: dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    index_map: dict[str | int, int],
) -> SteadyStateReaction:
    updated_steady_state_concentration = substitute(self.steady_state_concentration, template_map)
    updated_half_life = substitute(self.half_life, template_map)
    updated_volume = substitute(self.volume, template_map) if self.volume is not None else None
    new_steady_state_concentration = render(updated_steady_state_concentration, index_map)
    new_half_life = render(updated_half_life, index_map)
    new_volume = render(updated_volume, index_map) if updated_volume is not None else None
    return SteadyStateReaction(
        reactants=new_reactants,
        products=new_products,
        steady_state_concentration=new_steady_state_concentration,
        half_life=new_half_life,
        volume=new_volume,
    )
