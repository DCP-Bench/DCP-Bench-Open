import pulp


def build(instance):
    budget, npv, cash_flow = instance["budget"], instance["npv"], instance["cash_flow"]
    problem = pulp.LpProblem("capital_budget", pulp.LpMaximize)
    chosen = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(npv))]
    total = pulp.LpVariable("z", 0, sum(npv), cat="Integer")
    problem += pulp.lpSum(c * x for c, x in zip(cash_flow, chosen)) <= budget
    problem += total == pulp.lpSum(v * x for v, x in zip(npv, chosen))
    problem += total
    return problem, {"z": total, "x": chosen}
