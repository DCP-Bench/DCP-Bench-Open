# Hidato: fill a grid with the numbers 1..r*c, each once, so that consecutive numbers sit
# in cells that touch horizontally, vertically or diagonally; some numbers are given.
import cpmpy as cp


def build(instance):
    puzzle = instance["puzzle"]      # puzzle[i][j] is the given number, or 0 for an empty cell
    r, c = len(puzzle), len(puzzle[0])
    n = r * c

    # x[i][j] is the number written in cell (i, j).
    x = cp.intvar(1, n, shape=(r, c), name="x")

    # Helper variables. Cells are numbered row by row, 0..n-1. at_cell[q] is the number
    # (counted from 0) in cell q, and where_is[k] is the cell holding number k+1. The two
    # arrays are inverse permutations of each other, which also makes all numbers differ.
    at_cell = cp.intvar(0, n - 1, shape=n, name="at_cell")
    where_is = cp.intvar(0, n - 1, shape=n, name="where_is")

    model = cp.Model()

    # Link the grid to the helper array.
    for i in range(r):
        for j in range(c):
            model += x[i, j] == at_cell[i * c + j] + 1

    # Every number 1..n appears in exactly one cell.
    model += cp.Inverse(where_is, at_cell)

    # The numbers given at the start are fixed.
    for i in range(r):
        for j in range(c):
            if puzzle[i][j] > 0:
                model += x[i, j] == puzzle[i][j]

    # Consecutive numbers k and k+1 are in different cells that touch, including diagonally.
    # A table of the allowed (cell of k, cell of k+1) pairs states this directly.
    touching = [[i * c + j, (i + a) * c + (j + b)]
                for i in range(r) for j in range(c)
                for a in (-1, 0, 1) for b in (-1, 0, 1)
                if (a != 0 or b != 0) and 0 <= i + a < r and 0 <= j + b < c]
    for k in range(n - 1):
        model += cp.Table([where_is[k], where_is[k + 1]], touching)

    return model, {"x": x}
