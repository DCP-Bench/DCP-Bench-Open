"""Heterosquare: fill an n-by-n square with 1..n^2, each once, so that all row, column and diagonal sums differ."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    cells = [(i, j) for i in range(n) for j in range(n)]
    values = range(1, n * n + 1)

    model = gp.Model("heterosquare")

    # holds[i, j, v] is 1 when cell (i, j) holds v. Every cell holds one number
    # and every number 1..n^2 is used once, so the entries are all different.
    holds = model.addVars([(i, j, v) for (i, j) in cells for v in values], vtype=GRB.BINARY, name="holds")
    for (i, j) in cells:
        model.addConstr(holds.sum(i, j, "*") == 1, name=f"cell[{i},{j}]")
    for v in values:
        model.addConstr(holds.sum("*", "*", v) == 1, name=f"value[{v}]")
    x = [[gp.quicksum(v * holds[i, j, v] for v in values) for j in range(n)] for i in range(n)]

    # The 2n + 2 line sums: rows, columns, then the two diagonals.
    lines = ([gp.quicksum(x[i]) for i in range(n)]
             + [gp.quicksum(x[i][j] for i in range(n)) for j in range(n)]
             + [gp.quicksum(x[i][i] for i in range(n)), gp.quicksum(x[i][n - 1 - i] for i in range(n))])

    # All line sums differ: for each pair, a binary says which one is larger.
    for a in range(len(lines)):
        for b in range(a + 1, len(lines)):
            larger = model.addVar(vtype=GRB.BINARY, name=f"larger[{a},{b}]")
            model.addConstr((larger == 1) >> (lines[a] >= lines[b] + 1), name=f"a_larger[{a},{b}]")
            model.addConstr((larger == 0) >> (lines[b] >= lines[a] + 1), name=f"b_larger[{a},{b}]")

    return model, {"x": x}
