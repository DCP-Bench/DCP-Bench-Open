import pulp


def build(instance):
    """Fifty puzzle: knock over a set of dummies whose numbers total exactly
    the target sum.
    """
    values = instance["values"]
    target_sum = instance["target_sum"]
    n = len(values)

    problem = pulp.LpProblem("fifty", pulp.LpMinimize)
    dummies = [pulp.LpVariable(f"d{i}", cat="Binary") for i in range(n)]
    problem += pulp.lpSum(values[i] * dummies[i] for i in range(n)) == target_sum

    return problem, {"dummies": dummies}
