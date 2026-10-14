# Killer sudoku: fill an n-by-n grid with 1..n so that every row, column and box has
# each number once, and each cage (a group of cells) holds distinct numbers adding up
# to the small number printed in its corner.
import math

import cpmpy as cp


def build(instance):
    n = instance["n"]                  # side of the grid
    cages = instance["problem"]        # each cage is [total, [[row, col], ...]] with 1-based cells
    box = math.isqrt(n)                # side of a box (3 for the usual 9x9 grid)

    x = cp.intvar(1, n, shape=(n, n), name="x")

    model = cp.Model()

    # Every row contains each number exactly once.
    for i in range(n):
        model += cp.AllDifferent(x[i, :])

    # Every column contains each number exactly once.
    for j in range(n):
        model += cp.AllDifferent(x[:, j])

    # Every box (box-by-box block of cells) contains each number exactly once.
    for bi in range(n // box):
        for bj in range(n // box):
            block = [x[r, c]
                     for r in range(bi * box, (bi + 1) * box)
                     for c in range(bj * box, (bj + 1) * box)]
            model += cp.AllDifferent(block)

    # Every cage adds up to its total, and no number appears twice inside a cage.
    for total, cells in cages:
        cage = [x[r - 1, c - 1] for r, c in cells]   # cage cells are 1-based in the data
        model += cp.sum(cage) == total
        model += cp.AllDifferent(cage)

    return model, {"x": x}
