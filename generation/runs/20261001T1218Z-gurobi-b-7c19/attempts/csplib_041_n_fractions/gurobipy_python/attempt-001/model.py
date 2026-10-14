"""Fractions (CSPLib 41): distinct non-zero digits A..I with A/BC + D/EF + G/HI = 1."""
import itertools

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: nine letters, digits 1..9, as stated.
LETTERS = "ABCDEFGHI"
DIGITS = range(1, 10)


def build(instance):
    model = gp.Model("n_fractions")
    # The equation multiplies up to three digits with coefficients up to 1000;
    # a tight integrality tolerance keeps a near-0 binary from leaking into it.
    model.Params.IntFeasTol = 1e-9

    # is_[L, v] = 1 when letter L is digit v; digit[L] reads it back.
    is_ = model.addVars(LETTERS, DIGITS, vtype=GRB.BINARY, name="is")
    digit = {L: model.addVar(lb=1, ub=9, vtype=GRB.INTEGER, name=L) for L in LETTERS}
    for L in LETTERS:
        model.addConstr(is_.sum(L, "*") == 1, name=f"one_digit[{L}]")
        model.addConstr(digit[L] == gp.quicksum(v * is_[L, v] for v in DIGITS), name=f"read[{L}]")

    # The digits are distinct.
    for v in DIGITS:
        model.addConstr(is_.sum("*", v) <= 1, name=f"distinct[{v}]")

    def times(letter, expr, upper, name):
        """letter * expr for 0 <= expr <= upper, linear by disaggregating expr over
        the letter's one-hot digit: part[v] is expr when the letter is v, else 0."""
        part = model.addVars(DIGITS, lb=0, ub=upper, name=name)
        for v in DIGITS:
            model.addConstr(part[v] <= upper * is_[letter, v])
        model.addConstr(part.sum() == expr)
        return gp.quicksum(v * part[v] for v in DIGITS)

    # The reference declares each two-digit denominator in 1..9*9, so BC, EF
    # and HI are at most 81.
    for tens, units in (("B", "C"), ("E", "F"), ("H", "I")):
        model.addConstr(10 * digit[tens] + digit[units] <= 81, name=f"denominator[{tens}{units}]")

    # Clearing denominators turns the equation into
    #   A*EF*HI + D*BC*HI + G*BC*EF == BC*EF*HI,
    # whose expansion into digits is a sum of products of three distinct
    # letters. Each such product is built as letter * (letter * letter).
    pair_cache = {}

    def pair(x, y):
        key = tuple(sorted((x, y)))
        if key not in pair_cache:
            pair_cache[key] = times(key[0], digit[key[1]], 9, f"prod[{key[0]}{key[1]}]")
        return pair_cache[key]

    def triple(x, y, z):
        return times(x, pair(y, z), 81, f"prod[{x}{y}{z}]")

    def two_digit(tens, units):
        return [(10, tens), (1, units)]

    BC, EF, HI = two_digit("B", "C"), two_digit("E", "F"), two_digit("H", "I")

    def expand(numerator, first, second):
        """numerator * first * second, where first and second are two-digit numbers."""
        return gp.quicksum(c1 * c2 * triple(numerator, d1, d2)
                           for (c1, d1), (c2, d2) in itertools.product(first, second))

    left = expand("A", EF, HI) + expand("D", BC, HI) + expand("G", BC, EF)
    right = gp.quicksum(c1 * c2 * c3 * triple(d1, d2, d3)
                        for (c1, d1), (c2, d2), (c3, d3) in itertools.product(BC, EF, HI))

    # A / BC + D / EF + G / HI = 1, with the denominators cleared.
    model.addConstr(left == right, name="fractions_sum_to_one")

    return model, {L: digit[L] for L in LETTERS}
