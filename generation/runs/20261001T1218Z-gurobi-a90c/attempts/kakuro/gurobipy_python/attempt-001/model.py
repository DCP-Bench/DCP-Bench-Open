"""Kakuro: put a digit 1..9 in every white cell so that each entry sums to its clue with no digit repeated; blank cells hold 0."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    entries = instance["problem"]  # [clue, [row, col], [row, col], ...], 1-based cells
    blanks = instance["blanks"]  # [row, col], 1-based cells
    cells = range(n)
    digits = range(10)  # every cell holds 0..9

    model = gp.Model("kakuro")

    # is_[r, c, d] is 1 when cell (r, c) holds digit d; each cell holds one.
    is_ = model.addVars(cells, cells, digits, vtype=GRB.BINARY, name="is")
    for r in cells:
        for c in cells:
            model.addConstr(is_.sum(r, c, "*") == 1, name=f"cell[{r},{c}]")
    x = [[gp.quicksum(d * is_[r, c, d] for d in digits) for c in cells] for r in cells]

    # Blank cells are filled with 0.
    for k, (r, c) in enumerate(blanks):
        model.addConstr(is_[r - 1, c - 1, 0] == 1, name=f"blank[{k}]")

    for k, entry in enumerate(entries):
        clue = entry[0]
        segment = [(r - 1, c - 1) for r, c in entry[1:]]
        # Every cell of an entry holds a digit 1..9, not 0.
        for (r, c) in segment:
            model.addConstr(is_[r, c, 0] == 0, name=f"positive[{k},{r},{c}]")
        # The digits of an entry sum to its clue.
        model.addConstr(gp.quicksum(x[r][c] for r, c in segment) == clue, name=f"clue[{k}]")
        # No digit is repeated within an entry.
        for d in range(1, 10):
            model.addConstr(gp.quicksum(is_[r, c, d] for r, c in segment) <= 1, name=f"distinct[{k},{d}]")

    return model, {"x": x}
