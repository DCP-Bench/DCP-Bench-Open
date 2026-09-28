"""N-queens: place n queens on an n-by-n board so that no two share a row, a column or a diagonal."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    rows = range(n)
    cols = range(n)

    model = gp.Model("n_queens")

    # queen[i, j] is 1 when the queen of row i stands in column j.
    queen = model.addVars(rows, cols, vtype=GRB.BINARY, name="queen")

    # Every row has exactly one queen.
    for i in rows:
        model.addConstr(queen.sum(i, "*") == 1, name=f"row[{i}]")

    # No two queens share a column.
    for j in cols:
        model.addConstr(queen.sum("*", j) <= 1, name=f"col[{j}]")

    # No two queens share a diagonal: squares with the same j - i lie on one
    # diagonal, and squares with the same j + i on one anti-diagonal.
    for d in range(-(n - 1), n):
        model.addConstr(gp.quicksum(queen[i, i + d] for i in rows if 0 <= i + d < n) <= 1, name=f"diag[{d}]")
    for s in range(2 * n - 1):
        model.addConstr(gp.quicksum(queen[i, s - i] for i in rows if 0 <= s - i < n) <= 1, name=f"anti[{s}]")

    # The column, 1-based, of the queen in each row.
    return model, {"queens": [gp.quicksum((j + 1) * queen[i, j] for j in cols) for i in rows]}
