# Heterosquare of order n: fill an n x n square with the distinct integers 1 to n^2 so that
# the sums of the rows, the columns and the two diagonals are all different.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    N = n * n
    values = range(1, N + 1)
    cells = [(i, j) for i in range(n) for j in range(n)]
    m = Model("heterosquare")

    # b[i, j, v] = 1 if the square holds the element v at row i, column j
    b = {(i, j, v): m.addVar(name=f"b_{i}_{j}_{v}", vtype="B") for (i, j) in cells for v in values}

    # x[i, j] is the element at row i, column j
    x = {}
    for (i, j) in cells:
        # each cell holds exactly one element
        m.addCons(quicksum(b[i, j, v] for v in values) == 1)
        x[i, j] = m.addVar(name=f"x_{i}_{j}", vtype="I", lb=1, ub=N)
        m.addCons(x[i, j] == quicksum(v * b[i, j, v] for v in values))

    # the elements are distinct integers from 1 to n^2: each value is used exactly once
    for v in values:
        m.addCons(quicksum(b[i, j, v] for (i, j) in cells) == 1)

    # the sums of the rows, the columns and the two diagonals
    sums = {}
    for i in range(n):
        sums[f"row {i}"] = quicksum(x[i, j] for j in range(n))
    for j in range(n):
        sums[f"column {j}"] = quicksum(x[i, j] for i in range(n))
    sums["main diagonal"] = quicksum(x[i, i] for i in range(n))
    sums["anti-diagonal"] = quicksum(x[i, n - 1 - i] for i in range(n))

    # the sums are all different: each pair of sums differs, with a binary choosing the order
    names = list(sums)
    for a in range(len(names)):
        for c in range(a + 1, len(names)):
            sa, sc = sums[names[a]], sums[names[c]]
            d = m.addVar(name=f"order_{a}_{c}", vtype="B")
            m.addConsIndicator(sa - sc >= 1, binvar=d)
            m.addConsIndicator(sc - sa >= 1, binvar=d, activeone=False)

    square = [[x[i, j] for j in range(n)] for i in range(n)]
    return m, {"x": square}
