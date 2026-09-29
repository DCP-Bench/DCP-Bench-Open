# Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
# cells across or down) adds up to its clue and no digit repeats within an
# entry. Blank cells hold 0 in the answer.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]  # side of the grid
    entries = instance["problem"]  # [clue, [row, col], [row, col], ...] with cells counted from 1
    blanks = instance["blanks"]  # [row, col] of the cells that are blank

    model = cp_model.CpModel()

    # x[r][c] = digit in cell (r, c), or 0 for a blank cell
    x = [[model.new_int_var(0, 9, f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    # blank cells are 0
    for r, c in blanks:
        model.add(x[r - 1][c - 1] == 0)

    for clue, *cells in entries:
        run = [x[r - 1][c - 1] for r, c in cells]
        # the cells of an entry hold real digits, 1 to 9
        for cell in run:
            model.add(cell >= 1)
        # the digits of the entry add up to its clue
        model.add(sum(run) == clue)
        # no digit is repeated within an entry
        model.add_all_different(run)

    return model, {"x": x}
