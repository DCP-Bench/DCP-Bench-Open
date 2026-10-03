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

    # diffs[i] = |x[i+1] - x[i]|, an interval between 1 and n-1. The absolute value is
    # linearised by splitting each interval d into an upward step up[i][d] (x rises by
    # d) and a downward step down[i][d] (x falls by d); exactly one of the two is used
    # for each neighbouring pair, and no step of size 0 exists, so neighbours differ.
    up = pulp.LpVariable.dicts("up", (range(n - 1), range(1, n)), cat="Binary")
    down = pulp.LpVariable.dicts("down", (range(n - 1), range(1, n)), cat="Binary")
    diffs = [pulp.LpVariable(f"diffs_{i}", 1, n - 1, cat="Integer") for i in range(n - 1)]
    for i in range(n - 1):
        # every neighbouring pair has exactly one interval, going up or going down
        problem += pulp.lpSum(up[i][d] + down[i][d] for d in range(1, n)) == 1
        problem += diffs[i] == pulp.lpSum(d * (up[i][d] + down[i][d]) for d in range(1, n))
        # the step taken from x[i] to x[i+1] is +d for an upward step, -d for a downward one
        problem += x[i + 1] - x[i] == pulp.lpSum(d * (up[i][d] - down[i][d]) for d in range(1, n))
    for d in range(1, n):
        # the intervals are all different: each of 1..n-1 is used by exactly one pair
        problem += pulp.lpSum(up[i][d] + down[i][d] for i in range(n - 1)) == 1

    return problem, {"x": x, "diffs": diffs}
