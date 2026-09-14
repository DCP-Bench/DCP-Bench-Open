import pulp


def build(instance):
    denominations = instance["denominations"]
    ceiling = instance["max_amount_to_pay"]
    kinds = range(len(denominations))
    problem = pulp.LpProblem("coin3", pulp.LpMinimize)
    held = [pulp.LpVariable(f"x_{i}", 0, ceiling, cat="Integer") for i in kinds]
    for amount in range(1, ceiling):
        # A way of paying exactly this amount out of the coins held.
        paid = [pulp.LpVariable(f"pay_{amount}_{i}", 0, ceiling, cat="Integer") for i in kinds]
        problem += pulp.lpSum(denominations[i] * paid[i] for i in kinds) == amount
        for i in kinds:
            problem += paid[i] <= held[i]
    problem += pulp.lpSum(held)
    return problem, {"x": held}
