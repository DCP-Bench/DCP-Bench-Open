"""Killer sudoku: fill an n-by-n grid with 1..n so that rows, columns and boxes hold each number once, and every cage sums to its total with no repeated number."""
import math

import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # each cage is [total, [[row, col], ...]] with 1-based cells
    box = math.isqrt(n)  # boxes are box-by-box squares; 3 for the standard 9-by-9 grid
    cells = range(n)
    values = range(1, n + 1)

    model = gp.Model("killer_sudoku")

    # is_[r, c, v] is 1 when cell (r, c) holds number v; each cell holds one number.
    is_ = model.addVars(cells, cells, values, vtype=GRB.BINARY, name="is")
    for r in cells:
        for c in cells:
            model.addConstr(is_.sum(r, c, "*") == 1, name=f"cell[{r},{c}]")

    # Each row and each column contains each number exactly once.
    for v in values:
        for r in cells:
            model.addConstr(is_.sum(r, "*", v) == 1, name=f"row[{r},{v}]")
        for c in cells:
            model.addConstr(is_.sum("*", c, v) == 1, name=f"col[{c},{v}]")

    # Each box contains each number exactly once.
    for br in range(0, n, box):
        for bc in range(0, n, box):
            for v in values:
                model.addConstr(
                    gp.quicksum(is_[r, c, v] for r in range(br, br + box) for c in range(bc, bc + box)) == 1,
                    name=f"box[{br},{bc},{v}]",
                )

    x = [[gp.quicksum(v * is_[r, c, v] for v in values) for c in cells] for r in cells]

    # The numbers in a cage sum to its total, and no number appears twice in a cage.
    for k, (total, segment) in enumerate(cages):
        cage = [(r - 1, c - 1) for r, c in segment]
        model.addConstr(gp.quicksum(x[r][c] for r, c in cage) == total, name=f"cage_sum[{k}]")
        for v in values:
            model.addConstr(gp.quicksum(is_[r, c, v] for r, c in cage) <= 1, name=f"cage_distinct[{k},{v}]")

    return model, {"x": x}
