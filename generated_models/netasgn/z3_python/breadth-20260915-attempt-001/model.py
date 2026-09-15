import z3


def build(instance):
    supply, demand = instance["supply"], instance["demand"]
    cost, limit = instance["cost"], instance["limit"]
    people, projects = len(supply), len(demand)
    assign = [[z3.Int(f"a_{i}_{j}") for j in range(projects)] for i in range(people)]
    constraints = []
    for i in range(people):
        for j in range(projects):
            constraints += [assign[i][j] >= 0, assign[i][j] <= 10, assign[i][j] <= limit[i][j]]
        constraints.append(z3.Sum(assign[i]) == supply[i])
    for j in range(projects):
        constraints.append(z3.Sum([assign[i][j] for i in range(people)]) == demand[j])
    total = z3.Sum([cost[i][j] * assign[i][j] for i in range(people) for j in range(projects)])
    return constraints, {"assign": assign, "total_cost": total}, ("minimize", total)
