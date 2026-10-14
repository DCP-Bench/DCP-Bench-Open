# Car selection: assign participants to cars they are interested in, at most one car each and at most one participant per car, maximising the number of assignments.
from pyscipopt import Model, quicksum


def build(instance):
    interest = instance["possible_assignments"]
    n = len(interest)          # participants
    k = len(interest[0])       # cars

    m = Model()

    # a[i, j] = 1 if participant i is assigned to car j; only pairs the participant is interested in can be assigned
    a = {}
    for i in range(n):
        for j in range(k):
            a[i, j] = m.addVar(name=f"a_{i}_{j}", vtype="B", ub=1 if interest[i][j] == 1 else 0)

    # each participant is assigned to at most one car
    for i in range(n):
        m.addCons(quicksum(a[i, j] for j in range(k)) <= 1)

    # each car is assigned to at most one participant
    for j in range(k):
        m.addCons(quicksum(a[i, j] for i in range(n)) <= 1)

    # maximise the total number of assignments
    m.setObjective(quicksum(a[i, j] for i in range(n) for j in range(k)), "maximize")

    assignments = [[a[i, j] for j in range(k)] for i in range(n)]
    return m, {"assignments": assignments}
