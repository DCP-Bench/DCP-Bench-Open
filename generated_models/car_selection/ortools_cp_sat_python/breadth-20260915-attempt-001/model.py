from ortools.sat.python import cp_model


def build(instance):
    possible = instance["possible_assignments"]
    participants, cars = len(possible), len(possible[0])
    model = cp_model.CpModel()
    assigned = [[model.new_bool_var(f"a_{i}_{j}") for j in range(cars)] for i in range(participants)]
    for i in range(participants):
        for j in range(cars):
            model.add(assigned[i][j] <= possible[i][j])
        model.add_at_most_one(assigned[i])
    for j in range(cars):
        model.add_at_most_one(assigned[i][j] for i in range(participants))
    model.maximize(sum(assigned[i][j] for i in range(participants) for j in range(cars)))
    return model, {"assignments": assigned}
