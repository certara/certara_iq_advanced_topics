__all__ = ["Event"]

from dataclasses import dataclass

from ..expressions import Expression
from ..expressions.deparser import deparse_expression


@dataclass(frozen=True, slots=True)
class Event:
    """A concrete event with a trigger expression and one or more effects."""

    trigger: Expression
    effects: dict[str, Expression]

    def deparse(self) -> str:
        effect_strs = ", ".join(
            f"{effect_name} = {deparse_expression(effect)}" for effect_name, effect in self.effects.items()
        )
        return f"@({deparse_expression(self.trigger)}); {effect_strs}"
