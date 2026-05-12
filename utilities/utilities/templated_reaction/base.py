__all__ = ["TemplatedReaction"]


from dataclasses import dataclass

from ..templated_expressions import TemplatedName

# Reaction and its subtypes should not use slots because they need to use
# super() and it is broken with slots.
# https://treyhunner.com/2021/10/whats-great-about-python-3-dot-10/


@dataclass(frozen=True)
class TemplatedReaction:
    """Base class for templated reaction declarations."""

    reactants: list[TemplatedName]
    products: list[TemplatedName]
