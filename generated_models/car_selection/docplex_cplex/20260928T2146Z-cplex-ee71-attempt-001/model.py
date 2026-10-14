"""Car selection: assign participants to cars they are interested in, as many pairs as possible."""
from docplex.mp.model import Model


def build(instance):
    interested = instance["possible_assignments"]  # interested[i][j] is 1 if participant i likes car j
    participants = range(len(interested))
    cars = range(len(interested[0]))

    model = Model("car_selection")

    # assign[i, j] is 1 when participant i gets car j. A car the participant is
    # not interested in gets an upper bound of 0, so it can never be assigned.
    assign = model.binary_var_matrix(participants, cars, name="assign")
    for i in participants:
        for j in cars:
            assign[i, j].ub = interested[i][j]

    # Each participant is assigned to at most one car.
    for i in participants:
        model.add_constraint(model.sum(assign[i, j] for j in cars) <= 1, ctname=f"participant_{i}")

    # Each car is assigned to at most one participant.
    for j in cars:
        model.add_constraint(model.sum(assign[i, j] for i in participants) <= 1, ctname=f"car_{j}")

    # Maximise the number of assignments.
    model.maximize(model.sum(assign.values()))

    return model, {"assignments": [[assign[i, j] for j in cars] for i in participants]}
