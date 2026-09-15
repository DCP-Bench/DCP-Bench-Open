import z3


def build(instance):
    cost = instance["cost"]
    tasks, people = len(cost), len(cost[0])
    assigned = [[z3.Bool(f"x_{i}_{j}") for j in range(people)] for i in range(tasks)]
    picked = [[z3.If(assigned[i][j], 1, 0) for j in range(people)] for i in range(tasks)]
    constraints = []
    for i in range(tasks):
        constraints.append(z3.Sum(picked[i]) == 1)
    for j in range(people):
        constraints.append(z3.Sum([picked[i][j] for i in range(tasks)]) <= 1)
    objective = z3.Sum([cost[i][j] * picked[i][j] for i in range(tasks) for j in range(people)])
    return constraints, {"x": assigned}, ("minimize", objective)
