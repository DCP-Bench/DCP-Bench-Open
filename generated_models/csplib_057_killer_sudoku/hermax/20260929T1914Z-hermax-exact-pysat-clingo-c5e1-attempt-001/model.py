# Killer sudoku: fill a sudoku grid with 1..9 so that each row, column and 3x3
# box holds every digit once, and each cage of cells adds up to its target with
# no digit repeated inside the cage.
from math import isqrt

from hermax.model import Model


def build(instance):
    n = instance["n"]  # side of the grid
    cages = instance["problem"]  # [target sum, [[row, column], ...]] with cells counted from 1
    box = isqrt(n)  # side of a box

    m = Model()
    # x[r][c] = the digit in cell (r, c)
    x = m.int_matrix("x", n, n, 1, n)

    # each row and each column holds different digits
    for i in range(n):
        m &= x.row(i).all_different()
        m &= x.col(i).all_different()
    # each box holds different digits
    for i in range(box):
        for j in range(box):
            m &= m.vector([x[r][c] for r in range(i * box, (i + 1) * box)
                           for c in range(j * box, (j + 1) * box)]).all_different()

    # each cage adds up to its target and holds different digits
    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        m &= (sum(cage) == target)
        m &= m.vector(cage).all_different()

    return m, {"x": x}
