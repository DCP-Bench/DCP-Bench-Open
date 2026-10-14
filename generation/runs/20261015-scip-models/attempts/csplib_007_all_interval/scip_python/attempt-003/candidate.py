# All-interval series: arrange the pitch classes 0..n-1 in a sequence x so that the
# intervals between neighbouring notes |x[k+1] - x[k]| are exactly 1..n-1, each once.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    model = Model("all_interval")

    # Sequence of pitch classes: a permutation of 0..n-1.
    # One-hot binaries b[i, v]: position i holds pitch class v.
    b = {(i, v): model.addVar(name=f"pos_{i}_is_{v}", vtype="B") for i in range(n) for v in range(n)}
    x = [model.addVar(name=f"note_{i}", vtype="I", lb=0, ub=n - 1) for i in range(n)]
    # each position holds exactly one pitch class
    for i in range(n):
        model.addCons(quicksum(b[i, v] for v in range(n)) == 1)
        model.addCons(x[i] == quicksum(v * b[i, v] for v in range(n)))
    # each pitch class occurs exactly once
    for v in range(n):
        model.addCons(quicksum(b[i, v] for i in range(n)) == 1)

    # Intervals between neighbouring notes: d[k] = |x[k+1] - x[k]|, k = 0..n-2.
    # Values 1..n-1 are the possible intervals.
    d = [model.addVar(name=f"interval_{k}", vtype="I", lb=1, ub=n - 1) for k in range(n - 1)]
    # one-hot binaries e[k, v]: interval k has size v
    e = {(k, v): model.addVar(name=f"interval_{k}_is_{v}", vtype="B")
         for k in range(n - 1) for v in range(1, n)}
    for k in range(n - 1):
        model.addCons(quicksum(e[k, v] for v in range(1, n)) == 1)
        model.addCons(d[k] == quicksum(v * e[k, v] for v in range(1, n)))
        model.addCons(d[k] == abs(x[k + 1] - x[k]))
    # all intervals 1..n-1 occur, each exactly once
    # (n-1 intervals and n-1 possible sizes, so each size occurs exactly once)
    for v in range(1, n):
        model.addCons(quicksum(e[k, v] for k in range(n - 1)) == 1)

    # no objective: any all-interval series is a solution
    model.setObjective(0, "minimize")

    return model, {"x": x, "diffs": d}
