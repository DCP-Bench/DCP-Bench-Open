import pulp


def build(instance):
    values, weights = instance["values"], instance["weights"]
    capacity = instance["capacity"]
    problem = pulp.LpProblem("knapsack", pulp.LpMaximize)
    chosen = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(values))]
    problem += pulp.lpSum(w * x for w, x in zip(weights, chosen)) <= capacity
    problem += pulp.lpSum(v * x for v, x in zip(values, chosen))
    return problem, {"x": chosen}
