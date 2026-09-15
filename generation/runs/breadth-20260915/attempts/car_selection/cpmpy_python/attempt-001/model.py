import cpmpy as cp


def build(instance):
    possible = instance["possible_assignments"]
    participants, cars = len(possible), len(possible[0])
    assigned = cp.boolvar(shape=(participants, cars), name="assignments")
    model = cp.Model()
    for i in range(participants):
        for j in range(cars):
            model += assigned[i, j] <= possible[i][j]
        model += cp.sum([assigned[i, j] for j in range(cars)]) <= 1
    for j in range(cars):
        model += cp.sum([assigned[i, j] for i in range(participants)]) <= 1
    model.maximize(cp.sum([assigned[i, j] for i in range(participants) for j in range(cars)]))
    return model, {"assignments": [[assigned[i, j] for j in range(cars)] for i in range(participants)]}
