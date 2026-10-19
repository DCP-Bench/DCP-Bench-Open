# Assignment problem: assign people to 4 tasks with different costs so that the
# total cost is minimised. Each task goes to exactly one person, and not every
# person has to take a task. Output x[i][j] is True when task i is assigned to
# person j.
import mip


def build(instance):
    cost = instance["cost"]
    n_tasks = len(cost)
    n_people = len(cost[0])

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    x = [
        [model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(n_people)]
        for i in range(n_tasks)
    ]

    # Each task must be assigned to exactly one person.
    for i in range(n_tasks):
        model += mip.xsum(x[i][j] for j in range(n_people)) == 1

    # it is not necessary to assign all people to a task (each person takes at most one)
    for j in range(n_people):
        model += mip.xsum(x[i][j] for i in range(n_tasks)) <= 1

    # The total cost is minimised.
    model.objective = mip.xsum(
        cost[i][j] * x[i][j] for i in range(n_tasks) for j in range(n_people)
    )

    return model, {"x": x}
