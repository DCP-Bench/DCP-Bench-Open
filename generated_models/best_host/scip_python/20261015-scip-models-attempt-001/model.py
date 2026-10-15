# Best host: seat six guests around a round table so that as few neighbours
# as possible do not get along.
from pyscipopt import Model, quicksum

# Guests are numbered 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
# Each guest's list of the only people they will sit next to (from the statement).
# This is a fixed fact of the problem, not part of the instance.
GETS_ALONG = {
    0: {3, 5},  # Andrew: Dave, Frank
    1: {2, 4},  # Betty: Cara, Erica
    2: {1, 5},  # Cara: Betty, Frank
    3: {0, 4},  # Dave: Andrew, Erica
    4: {1, 3},  # Erica: Betty, Dave
    5: {0, 2},  # Frank: Andrew, Cara
}


def build(instance):
    n = 6
    m = Model()

    # b[i, g] = 1 if seat i is taken by guest g
    b = {(i, g): m.addVar(name=f"seat_{i}_guest_{g}", vtype="B")
         for i in range(n) for g in range(n)}

    # each seat holds exactly one guest, and each guest sits in exactly one seat
    for i in range(n):
        m.addCons(quicksum(b[i, g] for g in range(n)) == 1)
    for g in range(n):
        m.addCons(quicksum(b[i, g] for i in range(n)) == 1)

    # neighbours: seat i and the next seat round the table (the last seat wraps to the first)
    # p[i, g, h] = 1 if seat i has guest g and seat i+1 has guest h
    p = {(i, g, h): m.addVar(name=f"pair_{i}_{g}_{h}", vtype="B")
         for i in range(n) for g in range(n) for h in range(n)}
    for i in range(n):
        j = (i + 1) % n
        for g in range(n):
            m.addCons(quicksum(p[i, g, h] for h in range(n)) == b[i, g])
        for h in range(n):
            m.addCons(quicksum(p[i, g, h] for g in range(n)) == b[j, h])

    # a conflict is a pair of neighbours who do not get along; minimise their number
    # (each neighbouring pair of seats is counted once)
    conflicts = quicksum(p[i, g, h]
                         for i in range(n)
                         for g in range(n)
                         for h in range(n)
                         if h not in GETS_ALONG[g])
    m.setObjective(conflicts, "minimize")

    # the output lists the guest in each seat, in seating order
    x = [quicksum(g * b[i, g] for g in range(n)) for i in range(n)]
    return m, {"x": x}
