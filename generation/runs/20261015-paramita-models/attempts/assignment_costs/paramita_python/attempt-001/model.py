from paramita.modelling import Bool

# Assignment: assign people to tasks with different costs, so that the total cost
# is minimized. Each task is assigned to exactly one person, but not every person
# needs a task. x[i][j] is true when task i is assigned to person j.


def build(instance):
    cost = instance["cost"]
    n_tasks = len(cost)
    n_people = len(cost[0])

    x = [[Bool(f"x_{i}_{j}") for j in range(n_people)] for i in range(n_tasks)]
    cons = []

    # each task is assigned to exactly one person
    for i in range(n_tasks):
        cons.append(sum(x[i]) == 1)

    # each person does at most one task
    for j in range(n_people):
        cons.append(sum(x[i][j] for i in range(n_tasks)) <= 1)

    # total cost of the chosen task-person pairs
    total = sum(cost[i][j] * x[i][j] for i in range(n_tasks) for j in range(n_people))

    return cons, {"x": x}, ("minimize", total)
