# Car selection: assign participants to cars to maximize the total number of assignments.
# Each participant may be interested in a subset of cars (possible_assignments[i][j] == 1).
# Output assignments[i][j] is True if participant i is assigned to car j.
import mip


def build(instance):
    pa = instance["possible_assignments"]
    n_participants = len(pa)
    n_cars = len(pa[0]) if n_participants > 0 else 0

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # One binary per (participant, car) pair the participant is interested in.
    x = {}
    for i in range(n_participants):
        for j in range(n_cars):
            if pa[i][j] == 1:
                x[i, j] = model.add_var(f"x_{i}_{j}", var_type=mip.BINARY)

    # Each participant is assigned to at most one car.
    for i in range(n_participants):
        terms = [x[i, j] for j in range(n_cars) if (i, j) in x]
        if terms:
            model += mip.xsum(terms) <= 1

    # Each car is assigned to at most one participant.
    for j in range(n_cars):
        terms = [x[i, j] for i in range(n_participants) if (i, j) in x]
        if terms:
            model += mip.xsum(terms) <= 1

    # Objective: maximize the total number of assignments.
    model.objective = mip.xsum(x.values())

    assignments = [
        [x[i, j] if (i, j) in x else 0 for j in range(n_cars)]
        for i in range(n_participants)
    ]
    return model, {"assignments": assignments}
