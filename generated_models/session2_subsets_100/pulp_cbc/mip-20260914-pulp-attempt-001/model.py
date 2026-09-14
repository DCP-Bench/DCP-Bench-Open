import pulp


def build(instance):
    values = instance["A"]
    items = range(len(values))
    problem = pulp.LpProblem("subsets_100", pulp.LpMinimize)
    in_s = [pulp.LpVariable(f"s_{i}", cat="Binary") for i in items]
    in_t = [pulp.LpVariable(f"t_{i}", cat="Binary") for i in items]
    problem += (pulp.lpSum(values[i] * in_s[i] for i in items)
                == pulp.lpSum(values[i] * in_t[i] for i in items))
    for i in items:
        # No element lies in both subsets.
        problem += in_s[i] + in_t[i] <= 1
    problem += pulp.lpSum(in_s) >= 1
    problem += pulp.lpSum(in_t) >= 1
    return problem, {"in_S": in_s, "in_T": in_t}
