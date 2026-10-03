"""Pythagorean triplet (Project Euler 9): natural numbers a, b, c with a^2 + b^2 = c^2 and
a + b + c = 1000.

The model reports a, b and c.
"""
import pulp


def build(instance):
    del instance  # the problem has no instance data; its constants are below

    total = 1000  # a + b + c
    top = 500     # each number lies in 1..500, as in the reference
    values = range(1, top + 1)

    problem = pulp.LpProblem("pythagorean_triplet", pulp.LpMinimize)  # satisfaction

    # is_value[name][v] = 1 if the number is v. Squares are not linear, so each number is
    # chosen from its range and its square read off the same binaries.
    is_value = {name: {v: pulp.LpVariable(f"{name}_is_{v}", cat="Binary") for v in values}
                for name in "abc"}
    for name in "abc":
        problem += pulp.lpSum(is_value[name].values()) == 1
    number = {name: pulp.lpSum(v * var for v, var in is_value[name].items()) for name in "abc"}
    square = {name: pulp.lpSum(v * v * var for v, var in is_value[name].items()) for name in "abc"}

    # the three numbers add up to 1000
    problem += number["a"] + number["b"] + number["c"] == total

    # a^2 + b^2 = c^2
    problem += square["a"] + square["b"] == square["c"]

    return problem, number
