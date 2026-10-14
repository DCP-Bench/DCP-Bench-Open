"""All-interval series: arrange the pitch-classes 0..n-1 in a series x so that the n-1
absolute differences between neighbouring notes are exactly the intervals 1..n-1, each
once.

The model reports the series x and the interval vector diffs.
"""
import pulp


def build(instance):
    n = instance["n"]  # number of pitch-classes

    problem = pulp.LpProblem("all_interval", pulp.LpMinimize)  # satisfaction: no objective

    # x[i] = pitch-class at position i. All-different over 0..n-1 is stated as an
    # assignment matrix: pick[i][v] = 1 if position i holds pitch-class v.
    pick = pulp.LpVariable.dicts("pick", (range(n), range(n)), cat="Binary")
    x = [pulp.LpVariable(f"x_{i}", 0, n - 1, cat="Integer") for i in range(n)]
    for i in range(n):
        # each position holds exactly one pitch-class
        problem += pulp.lpSum(pick[i][v] for v in range(n)) == 1
        problem += x[i] == pulp.lpSum(v * pick[i][v] for v in range(n))
    for v in range(n):
        # each pitch-class occurs exactly once in the series
        problem += pulp.lpSum(pick[i][v] for i in range(n)) == 1

    # Neighbouring pairs. step[i][(u, v)] = 1 if x[i] = u and x[i+1] = v (u != v, since
    # the notes are all different). The pair is tied to the two positions it joins, which
    # makes the absolute difference |u - v| of the pair readable without a product or an
    # absolute value. step is continuous: once pick is 0/1, the two sums below leave a
    # single (u, v) with step 1, so step is integral on its own.
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    step = {(i, u, v): pulp.LpVariable(f"step_{i}_{u}_{v}", 0, 1)
            for i in range(n - 1) for (u, v) in pairs}
    for i in range(n - 1):
        for u in range(n):
            # the pair leaves from the pitch-class at position i
            problem += pulp.lpSum(step[(i, u, v)] for v in range(n) if v != u) == pick[i][u]
        for v in range(n):
            # the pair arrives at the pitch-class at position i + 1
            problem += pulp.lpSum(step[(i, u, v)] for u in range(n) if u != v) == pick[i + 1][v]

    # diffs[i] = |x[i+1] - x[i]|, an interval between 1 and n-1. Each interval d is used by
    # exactly one neighbouring pair (the intervals are all different, and there are n-1 of
    # them for the n-1 values 1..n-1).
    diffs = [pulp.LpVariable(f"diffs_{i}", 1, n - 1, cat="Integer") for i in range(n - 1)]
    for i in range(n - 1):
        problem += diffs[i] == pulp.lpSum(
            abs(u - v) * step[(i, u, v)] for (u, v) in pairs)
    for d in range(1, n):
        problem += pulp.lpSum(
            step[(i, u, v)] for i in range(n - 1) for (u, v) in pairs if abs(u - v) == d) == 1

    return problem, {"x": x, "diffs": diffs}
