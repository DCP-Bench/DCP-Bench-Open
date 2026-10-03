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

    digits = max_val.bit_length()  # enough binary digits to write max_val

    # a and n are written in binary digits: digit k of a is worth 2**k. The digits make the
    # products a * b and n * n linear (see below), because CPLEX refuses a product of two
    # integer variables as a non-convex quadratic constraint.
    a_bit = [model.binary_var(name=f"a_bit{k}") for k in range(digits)]
    n_bit = [model.binary_var(name=f"n_bit{k}") for k in range(digits)]
    a = model.sum((2 ** k) * a_bit[k] for k in range(digits))
    n = model.integer_var(0, max_val, name="n")
    b = model.integer_var(1, max_val, name="b")  # b is larger than 0
    model.add_range(min_a, a, max_val)
    model.add_constraint(n == model.sum((2 ** k) * n_bit[k] for k in range(digits)))

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

    def digit_times(digit, number, name):
        """A variable equal to digit * number, for a 0/1 digit and a number in 0..max_val."""
        product = model.integer_var(0, max_val, name=name)
        model.add_constraint(product <= max_val * digit)
        model.add_constraint(product <= number)
        model.add_constraint(product >= number - max_val * (1 - digit))
        return product

    # a * b is a perfect square: a * b = n * n. Writing a and n in binary digits,
    # a * b is the sum over the digits of a of 2**k times (digit k times b), and n * n is the
    # sum over the digits of n of 2**k times (digit k times n). Each digit times a number is
    # linear to state, so the equality is linear.
    a_times_b = model.sum((2 ** k) * digit_times(a_bit[k], b, f"a_bit{k}_times_b")
                          for k in range(digits))
    n_squared = model.sum((2 ** k) * digit_times(n_bit[k], n, f"n_bit{k}_times_n")
                          for k in range(digits))
    model.add_constraint(a_times_b == n_squared)

    # Objective: the smallest a.
    model.minimize(a)

    return model, {"a": a, "b": b, "n": n, "p": p}
