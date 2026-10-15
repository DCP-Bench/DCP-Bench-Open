# N-queens: place n queens on an n x n board so that no two share a row, column or diagonal.

from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = Model()

    # b[r, c] = 1 if a queen stands on row r, column c
    b = {(r, c): m.addVar(name=f"b_{r}_{c}", vtype="B") for r in range(n) for c in range(n)}

    # each row holds exactly one queen
    for r in range(n):
        m.addCons(quicksum(b[r, c] for c in range(n)) == 1, name=f"row_{r}")

    # each column holds exactly one queen
    for c in range(n):
        m.addCons(quicksum(b[r, c] for r in range(n)) == 1, name=f"col_{c}")

    # no two queens on the same diagonal (row - column constant)
    for d in range(-(n - 1), n):
        cells = [b[r, r - d] for r in range(n) if 0 <= r - d < n]
        if len(cells) > 1:
            m.addCons(quicksum(cells) <= 1, name=f"diag_{d}")

    # no two queens on the same anti-diagonal (row + column constant)
    for s in range(2 * n - 1):
        cells = [b[r, s - r] for r in range(n) if 0 <= s - r < n]
        if len(cells) > 1:
            m.addCons(quicksum(cells) <= 1, name=f"antidiag_{s}")

    # queens[i] = column of the queen in row i, numbered from 1
    queens = [quicksum((c + 1) * b[r, c] for c in range(n)) for r in range(n)]
    return m, {"queens": queens}
