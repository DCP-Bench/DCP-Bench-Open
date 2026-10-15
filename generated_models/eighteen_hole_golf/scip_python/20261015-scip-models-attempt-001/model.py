# Eighteen-hole golf course: choose a length of 3, 4 or 5 for each of 18 holes so that the lengths sum to 72.
from pyscipopt import Model, quicksum


def build(instance):
    # number of holes is fixed by the problem statement (18 holes)
    n_holes = 18
    # every hole has length 3, 4 or 5 (problem statement)
    lengths = [3, 4, 5]
    # the total length of the course is 72 (problem statement)
    total_length = 72

    m = Model()

    # one-hot choice: b[i, v] = 1 if hole i has length v
    b = {(i, v): m.addVar(name=f"b_{i}_{v}", vtype="B") for i in range(n_holes) for v in lengths}
    holes = [m.addVar(name=f"hole_{i}", lb=3, ub=5, vtype="I") for i in range(n_holes)]

    # each hole has exactly one length
    for i in range(n_holes):
        # each hole has exactly one length from 3, 4 or 5
        m.addCons(quicksum(b[i, v] for v in lengths) == 1)
        # the length of hole i is the chosen value
        m.addCons(holes[i] == quicksum(v * b[i, v] for v in lengths))

    # the total length of the course is 72
    m.addCons(quicksum(holes) == total_length)

    return m, {"holes": holes}
