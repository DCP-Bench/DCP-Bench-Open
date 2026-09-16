import pulp


def build(instance):
    """Split A into two disjoint non-empty subsets S and T with equal sums."""
    a = instance["A"]
    n = len(a)

    problem = pulp.LpProblem("subsets", pulp.LpMinimize)
    in_s = [pulp.LpVariable(f"s{i}", cat="Binary") for i in range(n)]
    in_t = [pulp.LpVariable(f"t{i}", cat="Binary") for i in range(n)]

    problem += (pulp.lpSum(a[i] * in_s[i] for i in range(n))
                == pulp.lpSum(a[i] * in_t[i] for i in range(n)))
    # Disjoint: no element lands in both subsets.
    for i in range(n):
        problem += in_s[i] + in_t[i] <= 1
    problem += pulp.lpSum(in_s) >= 1
    problem += pulp.lpSum(in_t) >= 1

    return problem, {"in_S": in_s, "in_T": in_t}
