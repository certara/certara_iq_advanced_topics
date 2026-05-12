__all__ = ["Reaction"]


from dataclasses import dataclass

# Reaction and its subtypes should not use slots because they need to use
# super() and it is broken with slots.
# https://treyhunner.com/2021/10/whats-great-about-python-3-dot-10/


@dataclass(frozen=True)
class Reaction:
    """Base class for concrete ReactionModel reaction declarations."""

    reactants: list[str]
    products: list[str]
