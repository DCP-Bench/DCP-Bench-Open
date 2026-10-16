"""Car selection: assign participants to cars they are interested in, maximising assignments.

Each participant can take at most one car and each car goes to at most one
participant. Assignments are Bools, so the constraints are cardinality (PB)
constraints over the Bools; no integer encoding is needed.
"""
from paramita.modelling import Bool


def build(instance):
    interest = instance["possible_assignments"]
    n = len(interest)
    m = len(interest[0])

    # a[i][j] is true when participant i is assigned to car j
    a = [[Bool(f"a_{i}_{j}") for j in range(m)] for i in range(n)]

    cons = []
    # a participant may only be assigned to a car they are interested in
    for i in range(n):
        for j in range(m):
            if interest[i][j] == 0:
                cons.append(~a[i][j])

    # each participant is assigned to at most one car
    for i in range(n):
        cons.append(sum(a[i]) <= 1)

    # each car is assigned to at most one participant
    for j in range(m):
        cons.append(sum(a[i][j] for i in range(n)) <= 1)

    # total number of assignments (objective and output)
    total = sum(a[i][j] for i in range(n) for j in range(m))

    return cons, {"assignments": a}, ("maximize", total)
