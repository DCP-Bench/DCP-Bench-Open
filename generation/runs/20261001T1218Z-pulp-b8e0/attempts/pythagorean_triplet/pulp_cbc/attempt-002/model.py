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

    a = pulp.LpVariable("a", 1, top, cat="Integer")
    b = pulp.LpVariable("b", 1, top, cat="Integer")
    c = pulp.LpVariable("c", 1, top, cat="Integer")

    # the three numbers add up to 1000
    problem += a + b + c == total

    # a^2 + b^2 = c^2. With c = 1000 - a - b this becomes
    #   a^2 + b^2 = (1000 - a - b)^2, that is  a * b = 1000 * (a + b) - 500000,
    # which leaves a single product instead of three squares.
    # The product is linearized by choosing a from its range: is_a[v] = 1 if a = v, and
    # share[v] is b when a = v and 0 otherwise, so that a * b = sum of v * share[v].
    is_a = {v: pulp.LpVariable(f"a_is_{v}", cat="Binary") for v in values}
    problem += pulp.lpSum(is_a.values()) == 1
    problem += a == pulp.lpSum(v * var for v, var in is_a.items())
    share = {v: pulp.LpVariable(f"share_{v}", 0, top) for v in values}
    for v, var in is_a.items():
        problem += share[v] <= top * var
        problem += share[v] <= b
        problem += share[v] >= b - top * (1 - var)
    problem += (pulp.lpSum(v * share[v] for v in values)
                == total * (a + b) - (total * total) // 2)

    return problem, {"a": a, "b": b, "c": c}
