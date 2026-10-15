# Appointment scheduling: assign each of the people to one interview slot,
# at most one person per slot, and only in slots where the person is free.
from pyscipopt import Model, quicksum


def build(instance):
    # m[i][j] = 1 if person i is free in slot j
    m_free = instance["m"]
    n_people = len(m_free)
    n_slots = len(m_free[0])

    model = Model()

    # x[i][j] = 1 if person i is assigned to slot j; a busy slot gets upper bound 0
    x = {
        (i, j): model.addVar(name=f"x_{i}_{j}", vtype="B", lb=0, ub=m_free[i][j])
        for i in range(n_people)
        for j in range(n_slots)
    }

    # each person is assigned to exactly one slot
    for i in range(n_people):
        model.addCons(quicksum(x[i, j] for j in range(n_slots)) == 1)

    # each slot holds at most one person
    for j in range(n_slots):
        model.addCons(quicksum(x[i, j] for i in range(n_people)) <= 1)

    # the output gives x[i][j] as booleans per person and slot
    outputs = {"x": [[x[i, j] for j in range(n_slots)] for i in range(n_people)]}
    return model, outputs
