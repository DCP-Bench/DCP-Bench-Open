"""N-fractions (CSPLib 41): find distinct non-zero digits A..I with
A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.

The model reports the nine digits.
"""
from itertools import permutations

import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    digits = range(1, 10)
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    problem = pulp.LpProblem("n_fractions", pulp.LpMinimize)  # satisfaction

    # term[k][(a, b, c)] = 1 if fraction k is a / (10 b + c), with its numerator and the
    # two digits of its denominator. A fraction of variables is not linear, so each of
    # the three fractions is chosen from the table of its possible digit triples and its
    # value is a coefficient of that choice.
    triples = list(permutations(digits, 3))
    term = [{t: pulp.LpVariable(f"term_{k}_{t[0]}{t[1]}{t[2]}", cat="Binary") for t in triples}
            for k in range(3)]
    for k in range(3):
        problem += pulp.lpSum(term[k].values()) == 1

    # the nine digits are all different: each digit appears in exactly one place
    for v in digits:
        problem += pulp.lpSum(var for k in range(3) for t, var in term[k].items()
                              if v in t) == 1

    # A/BC + D/EF + G/HI = 1. The fraction values are floating-point coefficients; every
    # choice of distinct digits that is not a solution misses 1 by at least 2.2e-4
    # (checked by enumerating all 9! digit orders), far above CBC's 1e-6 tolerances, so no
    # wrong choice can pass as a rounding error.
    problem += pulp.lpSum(t[0] / (10 * t[1] + t[2]) * var
                          for k in range(3) for t, var in term[k].items()) == 1

    # the digits A..I read off the chosen fractions
    outputs = {}
    for k in range(3):
        for place in range(3):
            outputs[names[3 * k + place]] = pulp.lpSum(t[place] * var
                                                       for t, var in term[k].items())
    return problem, outputs
