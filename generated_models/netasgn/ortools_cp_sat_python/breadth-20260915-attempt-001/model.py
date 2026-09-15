from ortools.sat.python import cp_model


def build(instance):
    supply, demand = instance["supply"], instance["demand"]
    cost, limit = instance["cost"], instance["limit"]
    people, projects = len(supply), len(demand)
    model = cp_model.CpModel()
    assign = [[model.new_int_var(0, 10, f"a_{i}_{j}") for j in range(projects)] for i in range(people)]
    for i in range(people):
        model.add(sum(assign[i]) == supply[i])
    for j in range(projects):
        model.add(sum(assign[i][j] for i in range(people)) == demand[j])
    for i in range(people):
        for j in range(projects):
            model.add(assign[i][j] <= limit[i][j])
    total = sum(cost[i][j] * assign[i][j] for i in range(people) for j in range(projects))
    model.minimize(total)
    return model, {"assign": assign, "total_cost": total}
