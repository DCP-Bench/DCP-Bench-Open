# Killer sudoku: fill a sudoku grid with 1..9 so that each row, column and 3x3
# box holds every digit once, and each cage of cells adds up to its target with
# no digit repeated inside the cage.
from math import isqrt

import z3


def build(instance):
    n = instance["n"]  # side of the grid
    cages = instance["problem"]  # [target sum, [[row, column], ...]] with cells counted from 1
    box = isqrt(n)  # side of a box

    solver = z3.Solver()

    # x[r][c] = the digit in cell (r, c)
    x = [[z3.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            solver.add(x[r][c] >= 1, x[r][c] <= n)

    # each row and each column holds different digits
    for r in range(n):
        solver.add(z3.Distinct(x[r]))
    for c in range(n):
        solver.add(z3.Distinct([x[r][c] for r in range(n)]))

    # each box holds different digits
    for i in range(box):
        for j in range(box):
            solver.add(z3.Distinct([x[r][c] for r in range(i * box, (i + 1) * box) for c in range(j * box, (j + 1) * box)]))

    # each cage adds up to its target and holds different digits
    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        solver.add(z3.Sum(cage) == target)
        solver.add(z3.Distinct(cage))

    return solver, {"x": x}
