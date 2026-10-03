"""Hardy 1729 squares: four different numbers a, b, c, d between 1 and 100 with
a^2 + b^2 = c^2 + d^2.

The model reports a, b, c and d.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its range is below

    range_min, range_max = 1, 100  # the numbers lie in 1..100
    values = range(range_min, range_max + 1)
    names = ["a", "b", "c", "d"]

    problem = pulp.LpProblem("hardy_1729_square", pulp.LpMinimize)  # satisfaction

    # is_value[x][v] = 1 if number x is v. Squares are not linear, so each number is chosen
    # from its range and its square read off the same binaries.
    is_value = {x: {v: pulp.LpVariable(f"{x}_is_{v}", cat="Binary") for v in values}
                for x in names}
    for x in names:
        problem += pulp.lpSum(is_value[x].values()) == 1
    number = {x: pulp.lpSum(v * var for v, var in is_value[x].items()) for x in names}
    square = {x: pulp.lpSum(v * v * var for v, var in is_value[x].items()) for x in names}

    # the four numbers are all different
    for v in values:
        problem += pulp.lpSum(is_value[x][v] for x in names) <= 1

    # the sum of the squares of the first two equals the sum of the squares of the other two
    problem += square["a"] + square["b"] == square["c"] + square["d"]

    return problem, number
