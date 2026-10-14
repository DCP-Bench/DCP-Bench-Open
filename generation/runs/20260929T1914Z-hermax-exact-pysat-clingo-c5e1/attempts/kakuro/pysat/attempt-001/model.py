# Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
# cells across or down) adds up to its clue and no digit repeats within an
# entry. Blank cells hold 0 in the answer.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]  # side of the grid
    entries = instance["problem"]  # [clue, [row, col], [row, col], ...] with cells counted from 1
    blanks = instance["blanks"]  # [row, col] of the cells that are blank

    pool = IDPool()
    # x[r][c] = digit in cell (r, c), or 0 for a blank cell
    x = [[Integer(f"x_{r}_{c}", 0, 9, vpool=pool) for c in range(n)] for r in range(n)]
    engine = IntegerEngine(vars=[cell for row in x for cell in row], vpool=pool)

    # blank cells are 0
    for r, c in blanks:
        engine.add_linear(x[r - 1][c - 1] == 0)

    for clue, *cells in entries:
        run = [x[r - 1][c - 1] for r, c in cells]
        # the cells of an entry hold real digits, 1 to 9
        for cell in run:
            engine.add_linear(cell >= 1)
        # the digits of the entry add up to its clue
        engine.add_linear(sum(run) == clue)
        # no digit is repeated within an entry
        engine.add_alldifferent(run)

    return engine.clausify(), {"x": x}
