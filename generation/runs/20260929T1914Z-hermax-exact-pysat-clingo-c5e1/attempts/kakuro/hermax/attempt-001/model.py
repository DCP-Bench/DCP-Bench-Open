# Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
# cells across or down) adds up to its clue and no digit repeats within an
# entry. Blank cells hold 0 in the answer.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # side of the grid
    entries = instance["problem"]  # [clue, [row, col], [row, col], ...] with cells counted from 1
    blanks = instance["blanks"]  # [row, col] of the cells that are blank

    m = Model()
    # x[r][c] = digit in cell (r, c), or 0 for a blank cell
    x = m.int_matrix("x", n, n, 0, 9)

    # blank cells are 0
    for r, c in blanks:
        m &= (x[r - 1][c - 1] == 0)

    for clue, *cells in entries:
        run = [x[r - 1][c - 1] for r, c in cells]
        # the cells of an entry hold real digits, 1 to 9
        for cell in run:
            m &= cell.in_range(1, 9)
        # the digits of the entry add up to its clue
        m &= (sum(run) == clue)
        # no digit is repeated within an entry
        m &= m.vector(run).all_different()

    return m, {"x": x}
