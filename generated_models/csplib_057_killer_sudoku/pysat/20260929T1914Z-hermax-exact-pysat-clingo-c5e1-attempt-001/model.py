# Killer sudoku: fill a sudoku grid with 1..9 so that each row, column and 3x3
# box holds every digit once, and each cage of cells adds up to its target with
# no digit repeated inside the cage.
from math import isqrt

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]  # side of the grid
    cages = instance["problem"]  # [target sum, [[row, column], ...]] with cells counted from 1
    box = isqrt(n)  # side of a box

    pool = IDPool()
    # x[r][c] = the digit in cell (r, c)
    x = [[Integer(f"x_{r}_{c}", 1, n, vpool=pool) for c in range(n)] for r in range(n)]
    engine = IntegerEngine(vars=[cell for row in x for cell in row], vpool=pool)

    # each row and each column holds different digits
    for i in range(n):
        engine.add_alldifferent(x[i])
        engine.add_alldifferent([x[r][i] for r in range(n)])
    # each box holds different digits
    for i in range(box):
        for j in range(box):
            engine.add_alldifferent([x[r][c] for r in range(i * box, (i + 1) * box)
                                     for c in range(j * box, (j + 1) * box)])

    # each cage adds up to its target and holds different digits
    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        engine.add_linear(sum(cage) == target)
        engine.add_alldifferent(cage)

    return engine.clausify(), {"x": x}
