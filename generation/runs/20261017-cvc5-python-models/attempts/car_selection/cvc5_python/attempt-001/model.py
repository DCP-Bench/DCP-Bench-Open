# car_selection: assign participants to cars to maximize the total number of assignments.
# Each participant may be interested in a subset of the available cars.

import cvc5.pythonic as cz


def build(instance):
    interest = instance["possible_assignments"]
    n = len(interest)
    m = len(interest[0]) if n else 0

    assign = [[cz.Bool(f"a_{i}_{j}") for j in range(m)] for i in range(n)]
    constraints = []

    # Each participant may be assigned only to a car they are interested in.
    for i in range(n):
        for j in range(m):
            if interest[i][j] != 1:
                constraints.append(cz.Not(assign[i][j]))

    # Each participant is assigned to at most one car.
    for i in range(n):
        constraints.append(cz.Sum([cz.If(assign[i][j], 1, 0) for j in range(m)]) <= 1)

    # Each car is assigned to at most one participant.
    for j in range(m):
        constraints.append(cz.Sum([cz.If(assign[i][j], 1, 0) for i in range(n)]) <= 1)

    # Maximize the total number of assignments.
    total = cz.Sum([cz.If(assign[i][j], 1, 0) for i in range(n) for j in range(m)])

    return constraints, {"assignments": assign}, ("maximize", total)
