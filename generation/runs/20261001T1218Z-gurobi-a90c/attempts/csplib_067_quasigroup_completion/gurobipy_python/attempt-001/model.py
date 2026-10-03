"""Quasigroup completion: complete a partially filled N-by-N Latin square so that every row and column holds each of 1..N exactly once."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    N = instance["N"]
    start = instance["start"]  # given values; 0 marks an empty cell
    cells = range(N)
    values = range(1, N + 1)

    model = gp.Model("quasigroup_completion")

    # is_[i, j, v] is 1 when cell (i, j) holds v; each cell holds one value.
    is_ = model.addVars(cells, cells, values, vtype=GRB.BINARY, name="is")
    for i in cells:
        for j in cells:
            model.addConstr(is_.sum(i, j, "*") == 1, name=f"cell[{i},{j}]")

    # The pre-filled cells keep their starting values.
    for i in cells:
        for j in cells:
            if start[i][j] != 0:
                model.addConstr(is_[i, j, start[i][j]] == 1, name=f"given[{i},{j}]")

    # Each row and each column contains each value exactly once.
    for v in values:
        for i in cells:
            model.addConstr(is_.sum(i, "*", v) == 1, name=f"row[{i},{v}]")
        for j in cells:
            model.addConstr(is_.sum("*", j, v) == 1, name=f"col[{j},{v}]")

    puzzle = [[gp.quicksum(v * is_[i, j, v] for v in values) for j in cells] for i in cells]
    return model, {"puzzle": puzzle}
