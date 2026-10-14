"""CMO 2012: find the smallest a, not below a given minimum, such that a - b is a prime p and
a * b is a perfect square n * n, for some positive integer b.

All of a, b, n and p are at most max_val.
"""
from math import isqrt

from docplex.mp.model import Model


def build(instance):
    min_a = instance["min_a"]      # a must be at least this
    max_val = instance["max_val"]  # upper bound of a, b, n and p

    model = Model("cmo_2012")
    # a * b = n * n is a quadratic constraint, a product of variables, which is not convex.
    # CPLEX accepts it only if the factors are binaries (it linearizes those products) and it
    # is told to search for a global optimum. So a, b and n are written in binary digits.
    model.parameters.optimalitytarget = 3

    digits = max_val.bit_length()  # enough binary digits to write max_val

    def number(name, low, high):
        """A whole number between low and high, written in binary digits."""
        bit = [model.binary_var(name=f"{name}_bit{k}") for k in range(digits)]
        value = model.sum((2 ** k) * bit[k] for k in range(digits))
        model.add_range(low, value, high)
        return value, bit

    a, a_bit = number("a", min_a, max_val)
    b, b_bit = number("b", 1, max_val)  # b is larger than 0
    n, n_bit = number("n", 0, max_val)

    # p = a - b is a prime number: between 2 and max_val.
    p = a - b
    model.add_range(2, p, max_val)
    # p is prime when no d from 2 up to the square root of max_val divides it, unless p is d
    # itself. For each such d, p = d * quotient + remainder; the remainder is at least 1
    # (positive[d] is 1), or else p is at most d. A composite p fails for its smallest prime
    # factor d, since p > d and d divides it. This takes three variables per d, where a
    # variable for each of the primes below max_val would be over the Community Edition's
    # 1000 variables for max_val = 10000.
    for d in range(2, isqrt(max_val) + 1):
        quotient = model.integer_var(0, max_val // d, name=f"quotient_{d}")
        remainder = model.integer_var(0, d - 1, name=f"remainder_{d}")
        positive = model.binary_var(name=f"positive_{d}")
        model.add_constraint(p == d * quotient + remainder)
        model.add_constraint(remainder >= positive)
        model.add_constraint(p <= d + (max_val - d) * positive)

    # a * b is a perfect square: a * b = n * n. A product of two numbers in binary digits is
    # the sum over pairs of digits of 2**(k + l) times the product of the two digits; for n * n
    # the product of a digit with itself is the digit, so those terms are written once.
    a_times_b = model.sum((2 ** (k + l)) * (a_bit[k] * b_bit[l])
                          for k in range(digits) for l in range(digits))
    n_squared = (model.sum((4 ** k) * n_bit[k] for k in range(digits))
                 + 2 * model.sum((2 ** (k + l)) * (n_bit[k] * n_bit[l])
                                 for k in range(digits) for l in range(k + 1, digits)))
    model.add_constraint(a_times_b == n_squared)

    # Objective: the smallest a.
    model.minimize(a)

    return model, {"a": a, "b": b, "n": n, "p": p}
