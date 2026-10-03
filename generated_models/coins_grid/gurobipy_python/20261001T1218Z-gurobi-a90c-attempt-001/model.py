"""Coins grid: place coins on an n-by-n grid with exactly c coins in every row and column, minimising the squared horizontal distance of each coin from the diagonal."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]  # grid size
    c = instance["c"]  # coins per row and per column
    cells = range(n)

    model = gp.Model("coins_grid")

    # x[i, j] is 1 when there is a coin on row i, column j.
    x = model.addVars(cells, cells, vtype=GRB.BINARY, name="x")

    # Every row holds exactly c coins.
    for i in cells:
        model.addConstr(x.sum(i, "*") == c, name=f"row[{i}]")

    # Every column holds exactly c coins.
    for j in cells:
        model.addConstr(x.sum("*", j) == c, name=f"col[{j}]")

    # Cost of the placement: each coin costs the square of its column's distance from its row's
    # index, which is a constant per cell, so the objective is linear.
    z = gp.quicksum(x[i, j] * (i - j) * (i - j) for i in cells for j in cells)
    model.setObjective(z, GRB.MINIMIZE)

    return model, {"x": [[x[i, j] for j in cells] for i in cells], "z": z}
