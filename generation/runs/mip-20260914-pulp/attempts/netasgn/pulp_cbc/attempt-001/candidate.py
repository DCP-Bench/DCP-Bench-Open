import pulp


def build(instance):
    supply, demand = instance["supply"], instance["demand"]
    cost, limit = instance["cost"], instance["limit"]
    people, projects = range(len(supply)), range(len(demand))
    problem = pulp.LpProblem("netasgn", pulp.LpMinimize)
    assign = [[pulp.LpVariable(f"assign_{i}_{j}", 0, 10, cat="Integer") for j in projects]
              for i in people]
    for i in people:
        problem += pulp.lpSum(assign[i]) == supply[i]
    for j in projects:
        problem += pulp.lpSum(assign[i][j] for i in people) == demand[j]
    for i in people:
        for j in projects:
            problem += assign[i][j] <= limit[i][j]
    total = pulp.lpSum(cost[i][j] * assign[i][j] for i in people for j in projects)
    problem += total
    return problem, {"assign": assign, "total_cost": total}
