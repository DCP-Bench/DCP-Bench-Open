import pulp


def build(instance):
    count, qualified, cost = instance["nb_workers"], instance["Qualified"], instance["Cost"]
    problem = pulp.LpProblem("covering", pulp.LpMinimize)
    hired = [pulp.LpVariable(f"worker_{i}", cat="Binary") for i in range(count)]
    total = pulp.LpVariable("total_cost", 0, count * sum(cost), cat="Integer")
    problem += total == pulp.lpSum(cost[i] * hired[i] for i in range(count))
    for task in qualified:
        # The instance lists qualified workers 1-based.
        problem += pulp.lpSum(hired[worker - 1] for worker in task) >= 1
    problem += total
    return problem, {"total_cost": total, "workers": hired}
