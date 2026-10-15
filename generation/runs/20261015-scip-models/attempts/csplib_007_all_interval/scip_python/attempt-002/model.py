# All-interval series of size n: a permutation x of pitch-classes 0..n-1 whose
# neighbouring intervals (the absolute differences) are a permutation of 1..n-1.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = Model()

    # one-hot: xb[i, v] = 1 if pitch-class v is at position i of the series
    xb = {(i, v): m.addVar(name=f"xb_{i}_{v}", vtype="B") for i in range(n) for v in range(n)}
    # db[i, v] = 1 if the interval between positions i and i+1 is v
    db = {(i, v): m.addVar(name=f"db_{i}_{v}", vtype="B") for i in range(n - 1) for v in range(1, n)}
    # up[i] = 1 if the series rises from position i to position i+1
    up = [m.addVar(name=f"up_{i}", vtype="B") for i in range(n - 1)]

    x = [m.addVar(name=f"x_{i}", vtype="I", lb=0, ub=n - 1) for i in range(n)]
    d = [m.addVar(name=f"d_{i}", vtype="I", lb=1, ub=n - 1) for i in range(n - 1)]

    # each position holds exactly one pitch-class, and x[i] is that pitch-class
    for i in range(n):
        m.addCons(quicksum(xb[i, v] for v in range(n)) == 1)
        m.addCons(x[i] == quicksum(v * xb[i, v] for v in range(n)))
    # the series is a permutation of 0..n-1: each pitch-class occurs exactly once
    for v in range(n):
        m.addCons(quicksum(xb[i, v] for i in range(n)) == 1)

    # each interval slot holds exactly one interval
    for i in range(n - 1):
        m.addCons(quicksum(db[i, v] for v in range(1, n)) == 1)
        m.addCons(d[i] == quicksum(v * db[i, v] for v in range(1, n)))
    # the intervals are a permutation of 1..n-1: each interval size occurs exactly once
    for v in range(1, n):
        m.addCons(quicksum(db[i, v] for i in range(n - 1)) == 1)

    # the interval between neighbouring notes is the absolute difference of their pitch-classes;
    # written as two indicator-controlled equalities instead of abs(), which SCIP handles as nonlinear
    for i in range(n - 1):
        # if up[i] = 1: d[i] = x[i+1] - x[i], and x[i+1] > x[i]
        m.addConsIndicator(x[i + 1] - x[i] >= 1, binvar=up[i])
        m.addConsIndicator(d[i] - (x[i + 1] - x[i]) <= 0, binvar=up[i])
        m.addConsIndicator(d[i] - (x[i + 1] - x[i]) >= 0, binvar=up[i])
        # if up[i] = 0: d[i] = x[i] - x[i+1], and x[i+1] < x[i]
        m.addConsIndicator(x[i] - x[i + 1] >= 1, binvar=up[i], activeone=False)
        m.addConsIndicator(d[i] - (x[i] - x[i + 1]) <= 0, binvar=up[i], activeone=False)
        m.addConsIndicator(d[i] - (x[i] - x[i + 1]) >= 0, binvar=up[i], activeone=False)

    return m, {"diffs": d, "x": x}
