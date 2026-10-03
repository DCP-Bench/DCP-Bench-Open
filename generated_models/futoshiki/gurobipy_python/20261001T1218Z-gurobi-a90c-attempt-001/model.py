"""Futoshiki: fill a square grid with 1..size so that each row and column holds every number once, the given digits stay, and all inequalities between cells hold."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    values = instance["values"]  # given digits; 0 means not set
    lt = instance["lt"]  # [i1, j1, i2, j2], 1-based: cell (i1, j1) < cell (i2, j2)
    size = len(values)
    cells = range(size)
    digits = range(1, size + 1)

    model = gp.Model("futoshiki")

    # is_[r, c, v] is 1 when cell (r, c) holds v; each cell holds one number.
    is_ = model.addVars(cells, cells, digits, vtype=GRB.BINARY, name="is")
    for r in cells:
        for c in cells:
            model.addConstr(is_.sum(r, c, "*") == 1, name=f"cell[{r},{c}]")
    grid = [[gp.quicksum(v * is_[r, c, v] for v in digits) for c in cells] for r in cells]

    # The digits given at the start keep their values.
    for r in cells:
        for c in cells:
            if values[r][c] > 0:
                model.addConstr(is_[r, c, values[r][c]] == 1, name=f"given[{r},{c}]")

    # Each row and each column contains each number exactly once.
    for v in digits:
        for r in cells:
            model.addConstr(is_.sum(r, "*", v) == 1, name=f"row[{r},{v}]")
        for c in cells:
            model.addConstr(is_.sum("*", c, v) == 1, name=f"col[{c},{v}]")

    # Every inequality between neighbouring cells holds (strictly smaller).
    for k, (i1, j1, i2, j2) in enumerate(lt):
        model.addConstr(grid[i1 - 1][j1 - 1] <= grid[i2 - 1][j2 - 1] - 1, name=f"less[{k}]")

    return model, {"grid": grid}
