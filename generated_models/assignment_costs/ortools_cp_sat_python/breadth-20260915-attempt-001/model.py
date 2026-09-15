from ortools.sat.python import cp_model


def build(instance):
    cost = instance["cost"]
    tasks, people = len(cost), len(cost[0])
    model = cp_model.CpModel()
    assigned = [[model.new_bool_var(f"x_{i}_{j}") for j in range(people)] for i in range(tasks)]
    for i in range(tasks):
        model.add_exactly_one(assigned[i])
    for j in range(people):
        model.add_at_most_one(assigned[i][j] for i in range(tasks))
    model.minimize(sum(cost[i][j] * assigned[i][j] for i in range(tasks) for j in range(people)))
    return model, {"x": assigned}
