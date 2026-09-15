import cpmpy as cp


def build(instance):
    cost = instance["cost"]
    tasks, people = len(cost), len(cost[0])
    assigned = cp.boolvar(shape=(tasks, people), name="x")
    model = cp.Model()
    for i in range(tasks):
        model += cp.sum([assigned[i, j] for j in range(people)]) == 1
    for j in range(people):
        model += cp.sum([assigned[i, j] for i in range(tasks)]) <= 1
    model.minimize(cp.sum([cost[i][j] * assigned[i, j] for i in range(tasks) for j in range(people)]))
    return model, {"x": [[assigned[i, j] for j in range(people)] for i in range(tasks)]}
