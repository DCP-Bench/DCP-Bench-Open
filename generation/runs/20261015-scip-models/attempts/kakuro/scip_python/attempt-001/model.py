# Kakuro: fill each white cell with a digit from 1 to 9 so that the digits of
# each clue's run sum to the clue, and no digit repeats within a run.
from pyscipopt import Model, quicksum

# the puzzle's digits are 1 to 9 inclusive (problem constant)
DIGITS = range(1, 10)


def build(instance):
    # each run is [clue, cell, cell, ...] over the 1-based (row, column) cells
    runs = [(run[0], [tuple(cell) for cell in run[1:]]) for run in instance["problem"]]
    # white cells are the cells that belong to some run; the listed blanks are the others
    white = sorted({cell for _, cells in runs for cell in cells})
    n = instance["n"]

    m = Model("kakuro")

    # b[r, c, v] = 1 if white cell (r, c) holds digit v
    b = {(r, c, v): m.addVar(name=f"b_{r}_{c}_{v}", vtype="B") for (r, c) in white for v in DIGITS}
    x = {}
    # each white cell holds exactly one digit
    for r, c in white:
        m.addCons(quicksum(b[r, c, v] for v in DIGITS) == 1)
        x[r, c] = quicksum(v * b[r, c, v] for v in DIGITS)

    for clue, cells in runs:
        # the digits of a run add up to its clue
        m.addCons(quicksum(x[cell] for cell in cells) == clue)
        # no digit is duplicated in a run
        for v in DIGITS:
            m.addCons(quicksum(b[cell[0], cell[1], v] for cell in cells) <= 1)

    # the solution matrix: 0 for clue and black cells, the digit for white cells
    grid = [[x[r, c] if (r, c) in x else 0 for c in range(1, n + 1)] for r in range(1, n + 1)]
    return m, {"x": grid}
