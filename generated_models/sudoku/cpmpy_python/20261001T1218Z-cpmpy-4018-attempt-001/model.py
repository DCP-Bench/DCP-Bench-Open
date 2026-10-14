# Sudoku: complete a partly filled 9 x 9 grid with the digits 1..9 so that every row, every
# column and every 3 x 3 block holds each digit exactly once.
from math import isqrt

import cpmpy as cp


def build(instance):
    given = instance["input_grid"]  # given[i][j] is a digit 1..9, or 0 for an empty cell
    n = len(given)                  # 9 for a standard Sudoku
    box = isqrt(n)                  # side of a block: 3 for a standard Sudoku

    # grid[i, j] = the digit in row i, column j
    grid = cp.intvar(1, n, shape=(n, n), name="grid")

    model = cp.Model()

    # The digits that are given stay where they are.
    for i in range(n):
        for j in range(n):
            if given[i][j] != 0:
                model += grid[i, j] == given[i][j]

    # Every row holds each digit once.
    model += [cp.AllDifferent(row) for row in grid]

    # Every column holds each digit once.
    model += [cp.AllDifferent(col) for col in grid.T]

    # Every block holds each digit once.
    for i in range(0, n, box):
        for j in range(0, n, box):
            model += cp.AllDifferent(grid[i:i + box, j:j + box])

    return model, {"grid": grid}
