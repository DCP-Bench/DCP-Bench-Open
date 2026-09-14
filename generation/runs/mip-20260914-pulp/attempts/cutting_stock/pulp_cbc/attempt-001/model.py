import pulp


def build(instance):
    orders, pattern_yield = instance["orders"], instance["num_rolls_width"]
    patterns = range(instance["num_patterns"])
    problem = pulp.LpProblem("cutting_stock", pulp.LpMinimize)
    used = [pulp.LpVariable(f"pattern_{j}", 0, 100, cat="Integer") for j in patterns]
    for i in range(len(instance["widths"])):
        problem += pulp.lpSum(pattern_yield[j][i] * used[j] for j in patterns) >= orders[i]
    rolls = pulp.lpSum(used)
    problem += rolls
    return problem, {"patterns_used": used, "min_rolls_cut": rolls}
