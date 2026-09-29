# Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
# cells across or down) adds up to its clue and no digit repeats within an
# entry. Blank cells hold 0 in the answer.
from exact import Exact


def build(instance):
    n = instance["n"]  # side of the grid
    entries = instance["problem"]  # [clue, [row, col], [row, col], ...] with cells counted from 1
    blanks = instance["blanks"]  # [row, col] of the cells that are blank

    solver = Exact()
    # x[r][c] = digit in cell (r, c), or 0 for a blank cell
    x = [[f"x_{r}_{c}" for c in range(n)] for r in range(n)]
    # is_[r][c][d] is 1 exactly when cell (r, c) holds digit d (none for a 0), so
    # that "no digit repeats in an entry" is a count of at most one per digit
    is_ = [[{} for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            solver.addVariable(x[r][c], 0, 9)
            for d in range(1, 10):
                is_[r][c][d] = f"is_{r}_{c}_{d}"
                solver.addVariable(is_[r][c][d], 0, 1)
            solver.addConstraint([(1, is_[r][c][d]) for d in range(1, 10)], False, 0, True, 1)
            solver.addConstraint([(d, is_[r][c][d]) for d in range(1, 10)] + [(-1, x[r][c])], True, 0, True, 0)

    # blank cells are 0
    for r, c in blanks:
        solver.addConstraint([(1, x[r - 1][c - 1])], True, 0, True, 0)

    for clue, *cells in entries:
        run = [(r - 1, c - 1) for r, c in cells]
        # the cells of an entry hold real digits, 1 to 9: some digit indicator is set
        for r, c in run:
            solver.addConstraint([(1, is_[r][c][d]) for d in range(1, 10)], True, 1, True, 1)
        # the digits of the entry add up to its clue
        solver.addConstraint([(1, x[r][c]) for r, c in run], True, clue, True, clue)
        # no digit is repeated within an entry
        for d in range(1, 10):
            solver.addConstraint([(1, is_[r][c][d]) for r, c in run], False, 0, True, 1)

    return solver, {"x": x}
