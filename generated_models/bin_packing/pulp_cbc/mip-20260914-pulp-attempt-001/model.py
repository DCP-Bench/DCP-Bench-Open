import pulp


def build(instance):
    weights, capacity = instance["weights"], instance["capacity"]
    num_bins = instance["num_bins"]
    items = range(len(weights))
    problem = pulp.LpProblem("bin_packing", pulp.LpMinimize)
    bins = [pulp.LpVariable(f"bin_{j}", 0, num_bins - 1, cat="Integer") for j in items]
    # in_bin[j][i] is 1 exactly when item j is in bin i.
    in_bin = [[pulp.LpVariable(f"in_{j}_{i}", cat="Binary") for i in range(num_bins)] for j in items]
    for j in items:
        problem += pulp.lpSum(in_bin[j]) == 1
        problem += bins[j] == pulp.lpSum(i * in_bin[j][i] for i in range(num_bins))
    for i in items:
        if i < num_bins:
            problem += pulp.lpSum(weights[j] * in_bin[j][i] for j in items) <= capacity
    return problem, {"bins": bins}
