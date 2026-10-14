"""Giant cat army: starting from [0], extend the list by adding 5, adding 7 or taking the
square root of the last number, keeping every number distinct, integral and at most 60,
so that 2, 10 and 14 appear in that order. The list has 24 numbers and ends with 14.

The model reports the list x.
"""
import math

import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its constants are below

    maxval = 60  # every number is at most 60
    n = 24       # length of the list
    values = range(maxval + 1)
    places = range(n)

    problem = pulp.LpProblem("giant_cat_army", pulp.LpMinimize)  # satisfaction

    # holds[i][v] = 1 if the i-th number of the list is v
    holds = [[pulp.LpVariable(f"holds_{i}_{v}", cat="Binary") for v in values] for i in places]
    for i in places:
        problem += pulp.lpSum(holds[i]) == 1
    x = [pulp.lpSum(v * holds[i][v] for v in values) for i in places]

    # all numbers in the list are distinct
    for v in values:
        problem += pulp.lpSum(holds[i][v] for i in places) <= 1

    # the list starts with 0, its second number is 5 or 7, and it ends with 14
    problem += holds[0][0] == 1
    problem += holds[1][5] + holds[1][7] == 1
    problem += holds[n - 1][14] == 1

    # each next number is the previous one plus 5, plus 7, or its integer square root
    def successors(v):
        nxt = [w for w in (v + 5, v + 7) if w <= maxval]
        root = math.isqrt(v)
        if root * root == v:
            nxt.append(root)
        return nxt

    for i in range(n - 1):
        for v in values:
            problem += holds[i][v] <= pulp.lpSum(holds[i + 1][w] for w in successors(v))

    # 2 and 10 both appear, 2 at an earlier place than 10 (14 is last)
    problem += pulp.lpSum(holds[i][2] for i in places) == 1
    problem += pulp.lpSum(holds[i][10] for i in places) == 1
    problem += (pulp.lpSum(i * holds[i][2] for i in places) + 1
                <= pulp.lpSum(i * holds[i][10] for i in places))

    return problem, {"x": x}
