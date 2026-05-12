__all__ = ["float_equals", "float_divide", "float_power"]

import math

import numpy as np


def float_equals(left: float, right: float):
    """Float equals where NaN == NaN and -0.0. != 0.0."""
    if math.isnan(left):
        return math.isnan(right)
    elif left == 0.0 and right == 0.0:
        return math.copysign(1.0, left) == math.copysign(1.0, right)
    else:
        return left == right


def float_divide(left: float, right: float):
    """Float division that allows a 0.0 denominator."""
    # This is simply defers to NumPy on exception
    try:
        return left / right
    except ZeroDivisionError:
        with np.errstate(divide="ignore"):
            return float(np.divide(float(left), float(right)))


def float_power(left: float, right: float):
    """Float exponentiation that stays in the reals."""
    # David H does not fully agree with how np.float_power behaves at the edges,
    # but chooses to leave this for another time
    with np.errstate(divide="ignore"):
        # Cast inputs to float so that it does not crash on Python Fractions
        return float(np.float_power(float(left), float(right)))
