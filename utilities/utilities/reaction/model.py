from __future__ import annotations

__all__ = ["ReactionModel"]

from dataclasses import dataclass
from pathlib import Path

from ..units import Unit
from ..units import ast as uast
from .assignment import Assignment
from .base import Reaction
from .compartment import Compartment
from .event import Event
from .initialization import Initialization, InitialValue
from .parameter import Parameter
from .route import Route
from .state import State


@dataclass(frozen=True, slots=True)
class ReactionModel:
    """A concrete ReactionModel with fully expanded names and expressions."""

    parameters: dict[str, Parameter]
    assignments: dict[str, Assignment]
    compartments: dict[str, Compartment]
    states: dict[str, State]
    reactions: list[Reaction]
    routes: dict[str, Route]
    events: list[Event]
    initialization: Initialization = InitialValue()
    time_unit: Unit = uast.Dimensionless()

    def to_text(self, path: Path) -> None:
        """Write this concrete model to a ReactionModel text file."""

        from ..units.deparser import deparse_unit

        model_text = "%% ReactionModel@2"

        #  write the initialization
        model_text += f"\n\ninitialization = {self.initialization.deparse()}"

        # write model time unit
        model_text += f"\ntime_unit = {deparse_unit(self.time_unit)}"

        # write components
        model_text += "\n% components"

        # write parameters
        model_text += "\n\n # Parameters"
        for name, parameter in self.parameters.items():
            model_text += f"\n{parameter.deparse(name)}"

        # write assignments
        model_text += "\n\n # Assignments"
        for name, assignment in self.assignments.items():
            model_text += f"\n{assignment.deparse(name)}"

        # write compartments
        model_text += "\n\n # Compartments"
        for name, compartment in self.compartments.items():
            model_text += f"\n{compartment.deparse(name)}"

        # write states
        model_text += "\n\n # States"
        for name, state in self.states.items():
            model_text += f"\n{state.deparse(name)}"

        # write reactions
        model_text += "\n\n # Reactions"
        for reaction in self.reactions:
            model_text += f"\n{reaction.deparse()}"

        # write routes
        model_text += "\n\n # Routes"
        for name, route in self.routes.items():
            model_text += f"\n{route.deparse(name)}"

        # write events
        model_text += "\n\n # Events"
        for event in self.events:
            model_text += f"\n{event.deparse()}"

        # write the full model
        path.write_text(model_text, encoding="utf-8")
