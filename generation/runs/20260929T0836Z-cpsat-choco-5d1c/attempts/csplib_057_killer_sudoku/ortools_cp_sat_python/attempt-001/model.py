# Killer sudoku: fill a sudoku grid with 1..9 so that each row, column and 3x3
# box holds every digit once, and each cage of cells adds up to its target with
# no digit repeated inside the cage.
from math import isqrt

from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]  # side of the grid
    cages = instance["problem"]  # [target sum, [[row, column], ...]] with cells counted from 1
    box = isqrt(n)  # side of a box

    model = cp_model.CpModel()

    # x[r][c] = the digit in cell (r, c)
    x = [[model.new_int_var(1, n, f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    # each row and each column holds different digits
    for r in range(n):
        model.add_all_different(x[r])
    for c in range(n):
        model.add_all_different([x[r][c] for r in range(n)])

    # each box holds different digits
    for i in range(box):
        for j in range(box):
            model.add_all_different(
                [x[r][c] for r in range(i * box, (i + 1) * box) for c in range(j * box, (j + 1) * box)]
            )

    # each cage adds up to its target and holds different digits
    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        model.add(sum(cage) == target)
        model.add_all_different(cage)

    return model, {"x": x}
