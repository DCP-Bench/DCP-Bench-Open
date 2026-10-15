# Assign people to tasks at minimum total cost: each task gets exactly one person, each person at most one task.
from pyscipopt import Model, quicksum


def build(instance):
    cost = instance["cost"]
    n_tasks = len(cost)
    n_people = len(cost[0])

    m = Model()

    # x[i, j] = 1 if task i is assigned to person j
    x = {(i, j): m.addVar(name=f"x_{i}_{j}", vtype="B") for i in range(n_tasks) for j in range(n_people)}

    # each task is assigned to exactly one person
    for i in range(n_tasks):
        m.addCons(quicksum(x[i, j] for j in range(n_people)) == 1)

    # each person does at most one task (it is not necessary to assign all people)
    for j in range(n_people):
        m.addCons(quicksum(x[i, j] for i in range(n_tasks)) <= 1)

    # minimize the total cost of the assignments
    m.setObjective(quicksum(cost[i][j] * x[i, j] for i in range(n_tasks) for j in range(n_people)), "minimize")

    outputs = {
        "x": [[x[i, j] for j in range(n_people)] for i in range(n_tasks)],
    }
    return m, outputs
