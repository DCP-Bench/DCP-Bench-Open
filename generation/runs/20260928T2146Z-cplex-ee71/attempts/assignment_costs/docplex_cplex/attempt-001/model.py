"""Assignment: give every task to a different person at the least total cost; people may stay idle."""
from docplex.mp.model import Model


def build(instance):
    cost = instance["cost"]  # cost[i][j]: cost of person j doing task i
    tasks = range(len(cost))
    people = range(len(cost[0]))

    model = Model("assignment_costs")

    # x[i, j] is 1 when task i is assigned to person j.
    x = model.binary_var_matrix(tasks, people, name="x")

    # Each task is assigned to exactly one person.
    for i in tasks:
        model.add_constraint(model.sum(x[i, j] for j in people) == 1, ctname=f"task_{i}")

    # Each person takes at most one task.
    for j in people:
        model.add_constraint(model.sum(x[i, j] for i in tasks) <= 1, ctname=f"person_{j}")

    # Minimise the total cost of the assignment.
    model.minimize(model.sum(cost[i][j] * x[i, j] for i in tasks for j in people))

    return model, {"x": [[x[i, j] for j in people] for i in tasks]}
