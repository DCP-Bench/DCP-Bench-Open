# Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
# cells across or down) adds up to its clue and no digit repeats within an
# entry. Blank cells hold 0 in the answer.
import z3


def build(instance):
    n = instance["n"]  # side of the grid
    entries = instance["problem"]  # [clue, [row, col], [row, col], ...] with cells counted from 1
    blanks = instance["blanks"]  # [row, col] of the cells that are blank

    solver = z3.Solver()

    # x[r][c] = digit in cell (r, c), or 0 for a blank cell
    x = [[z3.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            solver.add(x[r][c] >= 0, x[r][c] <= 9)

    # blank cells are 0
    for r, c in blanks:
        solver.add(x[r - 1][c - 1] == 0)

    for clue, *cells in entries:
        run = [x[r - 1][c - 1] for r, c in cells]
        # the cells of an entry hold real digits, 1 to 9
        for cell in run:
            solver.add(cell >= 1)
        # the digits of the entry add up to its clue
        solver.add(z3.Sum(run) == clue)
        # no digit is repeated within an entry
        solver.add(z3.Distinct(run))

    return solver, {"x": x}
