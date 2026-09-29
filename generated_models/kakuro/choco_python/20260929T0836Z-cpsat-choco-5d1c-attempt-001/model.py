# Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
# cells across or down) adds up to its clue and no digit repeats within an
# entry. Blank cells hold 0 in the answer.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # side of the grid
    entries = instance["problem"]  # [clue, [row, col], [row, col], ...] with cells counted from 1
    blanks = instance["blanks"]  # [row, col] of the cells that are blank

    model = Model()

    # x[r][c] = digit in cell (r, c), or 0 for a blank cell
    x = [[model.intvar(0, 9, name=f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    # blank cells are 0
    for r, c in blanks:
        model.arithm(x[r - 1][c - 1], "=", 0).post()

    for clue, *cells in entries:
        run = [x[r - 1][c - 1] for r, c in cells]
        # the cells of an entry hold real digits, 1 to 9
        for cell in run:
            model.arithm(cell, ">=", 1).post()
        # the digits of the entry add up to its clue
        model.sum(run, "=", clue).post()
        # no digit is repeated within an entry
        model.all_different(run).post()

    return model, {"x": x}
