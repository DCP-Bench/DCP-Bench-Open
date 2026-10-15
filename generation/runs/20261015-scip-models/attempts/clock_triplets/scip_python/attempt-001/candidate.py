# Clock triplets: arrange the numbers 1 to 12 on the face of a clock so that no triplet of adjacent numbers has a sum higher than 21.
from pyscipopt import Model, quicksum

N = 12  # positions on the clock face and the numbers 1..N (problem constant, from the description)
MAX_TRIPLET_SUM = 21  # the bound from the description


def build(instance):
    m = Model()
    # b[p, v] = 1 if position p (0..11, clockwise from 12) holds the number v + 1
    b = {(p, v): m.addVar(name=f"b_{p}_{v}", vtype="B") for p in range(N) for v in range(N)}
    # each position holds exactly one number
    for p in range(N):
        # one number per position
        m.addCons(quicksum(b[p, v] for v in range(N)) == 1)
    # each number is used exactly once
    for v in range(N):
        # each number 1..12 appears exactly once on the clock
        m.addCons(quicksum(b[p, v] for p in range(N)) == 1)
    # value of each position, as an expression of the one-hot binaries
    x = [quicksum((v + 1) * b[p, v] for v in range(N)) for p in range(N)]
    # no triplet of adjacent numbers has a sum higher than 21 (the clock wraps around, so position 11 is adjacent to 0 and 1)
    for p in range(N):
        # triplet of adjacent numbers starting at this position
        m.addCons(x[p] + x[(p + 1) % N] + x[(p + 2) % N] <= MAX_TRIPLET_SUM)
    return m, {"x": x}
