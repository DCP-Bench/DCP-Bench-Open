import cpmpy as cp


def build(instance):
    supply, demand = instance["supply"], instance["demand"]
    cost, limit = instance["cost"], instance["limit"]
    people, projects = len(supply), len(demand)
    assign = cp.intvar(0, 10, shape=(people, projects), name="assign")
    model = cp.Model()
    for i in range(people):
        model += cp.sum([assign[i, j] for j in range(projects)]) == supply[i]
    for j in range(projects):
        model += cp.sum([assign[i, j] for i in range(people)]) == demand[j]
    for i in range(people):
        for j in range(projects):
            model += assign[i, j] <= limit[i][j]
    total = cp.sum([cost[i][j] * assign[i, j] for i in range(people) for j in range(projects)])
    model.minimize(total)
    return model, {"assign": [[assign[i, j] for j in range(projects)] for i in range(people)],
                   "total_cost": total}
