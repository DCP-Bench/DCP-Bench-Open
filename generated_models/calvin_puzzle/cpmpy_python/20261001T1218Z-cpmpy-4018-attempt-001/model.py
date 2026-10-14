# Calvin puzzle: fill an n x n grid with 1..n^2 so that each number is followed by the next one
# either exactly three squares away horizontally or vertically, or exactly two squares away
# along both axes (a diagonal jump of two).
import cpmpy as cp


def build(instance):
    n = instance["n"]
    cells = n * n

    # x[i, j] = the number written in row i, column j
    x = cp.intvar(1, cells, shape=(n, n), name="x")

    # The moves allowed by the rules (a fixed part of the puzzle): three squares along a row or
    # column, or two squares along both axes.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # All pairs (from cell, to cell) of grid squares, numbered row by row, that are one allowed
    # move apart.
    allowed = [(i * n + j, (i + di) * n + (j + dj))
               for i in range(n) for j in range(n) for di, dj in moves
               if 0 <= i + di < n and 0 <= j + dj < n]

    model = cp.Model()

    # Encoding choice: describe the grid by where each number sits, because the rule links
    # consecutive numbers. pos[k] = the square (row * n + column) holding the number k + 1, and
    # idx[c] = the number (from 0) in square c; the two are inverse permutations of each other.
    pos = cp.intvar(0, cells - 1, shape=(cells,), name="pos")
    idx = cp.intvar(0, cells - 1, shape=(cells,), name="idx")
    model += cp.Inverse(pos, idx)

    # Every number from 1 to n^2 is used exactly once (implied by the inverse permutation, and
    # stated for clarity).
    model += cp.AllDifferent(pos)

    # The number k + 1 sits one allowed move away from the number k.
    for k in range(cells - 1):
        model += cp.Table([pos[k], pos[k + 1]], allowed)

    # The grid shows, in each square, the number found there (numbers run from 1).
    for i in range(n):
        for j in range(n):
            model += x[i, j] == idx[i * n + j] + 1

    return model, {"x": x}
