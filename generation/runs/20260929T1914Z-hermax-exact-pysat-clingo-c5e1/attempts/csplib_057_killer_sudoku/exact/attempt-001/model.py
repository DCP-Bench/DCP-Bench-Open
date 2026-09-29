# Killer sudoku: fill a sudoku grid with 1..9 so that each row, column and 3x3
# box holds every digit once, and each cage of cells adds up to its target with
# no digit repeated inside the cage.
from math import isqrt

from exact import Exact


def build(instance):
    n = instance["n"]  # side of the grid
    cages = instance["problem"]  # [target sum, [[row, column], ...]] with cells counted from 1
    box = isqrt(n)  # side of a box

    solver = Exact()
    # x[r][c] = the digit in cell (r, c); is_[r][c][d] is 1 exactly when it holds d
    x = [[f"x_{r}_{c}" for c in range(n)] for r in range(n)]
    is_ = [[{} for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            solver.addVariable(x[r][c], 1, n)
            for d in range(1, n + 1):
                is_[r][c][d] = f"is_{r}_{c}_{d}"
                solver.addVariable(is_[r][c][d], 0, 1)
            solver.addConstraint([(1, is_[r][c][d]) for d in range(1, n + 1)], True, 1, True, 1)
            solver.addConstraint([(d, is_[r][c][d]) for d in range(1, n + 1)] + [(-1, x[r][c])], True, 0, True, 0)

    def at_most_once_each(cells):
        for d in range(1, n + 1):
            solver.addConstraint([(1, is_[r][c][d]) for r, c in cells], False, 0, True, 1)

    # each row, column and box holds different digits
    for i in range(n):
        at_most_once_each([(i, c) for c in range(n)])
        at_most_once_each([(r, i) for r in range(n)])
    for i in range(box):
        for j in range(box):
            at_most_once_each([(r, c) for r in range(i * box, (i + 1) * box)
                               for c in range(j * box, (j + 1) * box)])

    # each cage adds up to its target and holds different digits
    for target, cells in cages:
        cage = [(r - 1, c - 1) for r, c in cells]
        solver.addConstraint([(1, x[r][c]) for r, c in cage], True, target, True, target)
        at_most_once_each(cage)

    return solver, {"x": x}
