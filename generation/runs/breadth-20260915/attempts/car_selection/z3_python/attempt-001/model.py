import z3


def build(instance):
    possible = instance["possible_assignments"]
    participants, cars = len(possible), len(possible[0])
    assigned = [[z3.Bool(f"a_{i}_{j}") for j in range(cars)] for i in range(participants)]
    picked = [[z3.If(assigned[i][j], 1, 0) for j in range(cars)] for i in range(participants)]
    constraints = []
    for i in range(participants):
        for j in range(cars):
            constraints.append(picked[i][j] <= possible[i][j])
        constraints.append(z3.Sum(picked[i]) <= 1)
    for j in range(cars):
        constraints.append(z3.Sum([picked[i][j] for i in range(participants)]) <= 1)
    objective = z3.Sum([picked[i][j] for i in range(participants) for j in range(cars)])
    return constraints, {"assignments": assigned}, ("maximize", objective)
