import pulp


def build(instance):
    cost = instance["cost"]
    tasks, people = range(len(cost)), range(len(cost[0]))
    problem = pulp.LpProblem("assignment_costs", pulp.LpMinimize)
    assigned = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in people] for i in tasks]
    for i in tasks:
        problem += pulp.lpSum(assigned[i]) == 1
    for j in people:
        problem += pulp.lpSum(assigned[i][j] for i in tasks) <= 1
    problem += pulp.lpSum(cost[i][j] * assigned[i][j] for i in tasks for j in people)
    return problem, {"x": assigned}
