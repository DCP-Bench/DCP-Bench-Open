# Assignment problem: assign people to 4 tasks with different costs so that the
# total cost is minimised. Attempt 2: same formulation as attempt 1, re-evaluated
# under the corrected run profile (99 instances).

import cvc5.pythonic as cz


def build(instance):
    cost = instance["cost"]
    n_tasks = len(cost)
    n_people = len(cost[0])

    x = [[cz.Bool(f"x_{i}_{j}") for j in range(n_people)] for i in range(n_tasks)]

    constraints = []

    # Each task must be assigned to exactly one person, but it is not necessary to assign all people to a task.
    for i in range(n_tasks):
        constraints.append(cz.Sum([cz.If(x[i][j], 1, 0) for j in range(n_people)]) == 1)

    # Each person takes at most one task.
    for j in range(n_people):
        constraints.append(cz.Sum([cz.If(x[i][j], 1, 0) for i in range(n_tasks)]) <= 1)

    # The total cost of the assignment is minimised.
    total_cost = cz.Sum([cz.If(x[i][j], int(cost[i][j]), 0)
                         for i in range(n_tasks) for j in range(n_people)])

    return constraints, {"x": x}, ("minimize", total_cost)
