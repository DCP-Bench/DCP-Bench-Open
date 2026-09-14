import itertools

import pulp

# The reference's own bound on a single bale.
HEAVIEST = 50


def build(instance):
    n, weights = instance["n"], instance["weights"]
    problem = pulp.LpProblem("bales_of_hay", pulp.LpMinimize)
    bales = [pulp.LpVariable(f"bale_{i}", 0, HEAVIEST, cat="Integer") for i in range(n)]
    pairs = list(itertools.combinations(range(n), 2))
    slack = 2 * HEAVIEST + max(weights)
    for position, weight in enumerate(weights):
        chosen = {}
        for i, j in pairs:
            pick = pulp.LpVariable(f"pick_{position}_{i}_{j}", cat="Binary")
            chosen[(i, j)] = pick
            problem += bales[i] + bales[j] <= weight + slack * (1 - pick)
            problem += bales[i] + bales[j] >= weight - slack * (1 - pick)
        problem += pulp.lpSum(chosen.values()) == 1
    return problem, {"bales": bales}
