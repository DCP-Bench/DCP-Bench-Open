# Costas array problem: a permutation X of 1..n whose difference triangle has all-different lines.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = Model()
    values = range(1, n + 1)

    # X[i] is the mark's column in row i (1-based values), as a one-hot choice over 1..n
    b = {(i, v): m.addVar(name=f"b_{i}_{v}", vtype="B") for i in range(n) for v in values}
    X = [quicksum(v * b[i, v] for v in values) for i in range(n)]
    for i in range(n):
        # each row holds exactly one mark
        m.addCons(quicksum(b[i, v] for v in values) == 1)
    for v in values:
        # each column holds exactly one mark: X is a permutation
        m.addCons(quicksum(b[i, v] for i in range(n)) == 1)

    # difference values X[i+l] - X[i] range over -(n-1)..(n-1); zero is impossible in a permutation
    diffs = [d for d in range(-(n - 1), n) if d != 0]
    for l in range(1, n):
        # line l of the difference triangle: n-l differences X[i+l] - X[i]
        dv = {}
        for i in range(n - l):
            for d in diffs:
                dv[i, d] = m.addVar(name=f"d_{l}_{i}_{d + n}", vtype="B")
            # each difference takes exactly one value
            m.addCons(quicksum(dv[i, d] for d in diffs) == 1)
            # the difference variable equals the actual difference of the two marks
            m.addCons(quicksum(d * dv[i, d] for d in diffs) == X[i + l] - X[i])
        # all differences within line l are different
        # (line l must not contain any value twice)
        for d in diffs:
            m.addCons(quicksum(dv[i, d] for i in range(n - l)) <= 1)

    # the output gives the mark column of each row, numbered from 1
    return m, {"costas": X}
