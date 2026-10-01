# Kakuro: fill the white cells of a grid with digits 1..9 so that the digits of every
# entry (a run of cells) add up to its clue and no digit repeats within an entry.
# Black cells are shown as 0 in the answer.
import cpmpy as cp


def build(instance):
    n = instance["n"]                 # the grid is n by n
    entries = instance["problem"]     # each entry is [clue, [row, col], [row, col], ...] with 1-based cells
    blanks = instance["blanks"]       # [row, col] (1-based) of the black cells

    # Digit in each cell: 1..9 for white cells, 0 for black cells.
    x = cp.intvar(0, 9, shape=(n, n), name="x")

    model = cp.Model()

    # Black cells hold 0.
    for row, col in blanks:
        model += x[row - 1, col - 1] == 0

    for clue, *cells in entries:
        entry = [x[row - 1, col - 1] for row, col in cells]
        # Cells of an entry are white, so they hold a digit from 1 to 9 (not 0).
        for cell in entry:
            model += cell >= 1
        # The digits of the entry add up to its clue.
        model += cp.sum(entry) == clue
        # No digit is repeated within the entry.
        model += cp.AllDifferent(entry)

    return model, {"x": x}
