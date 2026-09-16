import pulp


def build(instance):
    """Steiner triple system: n(n-1)/6 triples drawn from n items, no two
    triples sharing more than one item.
    """
    n = instance["n"]
    n_sets = n * (n - 1) // 6

    problem = pulp.LpProblem("steiner", pulp.LpMinimize)
    sets = pulp.LpVariable.dicts("sets", (range(n_sets), range(n)),
                                 cat="Binary")

    for i in range(n_sets):
        problem += pulp.lpSum(sets[i][j] for j in range(n)) == 3

    # Two triples overlap in at most one item. The overlap indicator per item
    # is the conjunction of the two memberships, written the MIP way.
    for i in range(n_sets):
        for k in range(i + 1, n_sets):
            both = []
            for j in range(n):
                z = pulp.LpVariable(f"both_{i}_{k}_{j}", cat="Binary")
                problem += z <= sets[i][j]
                problem += z <= sets[k][j]
                problem += z >= sets[i][j] + sets[k][j] - 1
                both.append(z)
            problem += pulp.lpSum(both) <= 1

    rows = [[sets[i][j] for j in range(n)] for i in range(n_sets)]
    return problem, {"sets": rows}
