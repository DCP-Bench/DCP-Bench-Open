"""Car selection: assign participants to cars they are interested in, as many pairs as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    interested = instance["possible_assignments"]  # interested[i][j] is 1 if participant i likes car j
    participants = range(len(interested))
    cars = range(len(interested[0]))

    model = gp.Model("car_selection")

    # assign[i, j] is 1 when participant i gets car j. A car the participant is
    # not interested in gets an upper bound of 0, so it can never be assigned.
    assign = model.addVars(participants, cars, vtype=GRB.BINARY, name="assign")
    for i in participants:
        for j in cars:
            assign[i, j].UB = interested[i][j]

    # Each participant is assigned to at most one car.
    for i in participants:
        model.addConstr(assign.sum(i, "*") <= 1, name=f"participant[{i}]")

    # Each car is assigned to at most one participant.
    for j in cars:
        model.addConstr(assign.sum("*", j) <= 1, name=f"car[{j}]")

    # Maximise the number of assignments.
    model.setObjective(assign.sum(), GRB.MAXIMIZE)

    return model, {"assignments": [[assign[i, j] for j in cars] for i in participants]}
