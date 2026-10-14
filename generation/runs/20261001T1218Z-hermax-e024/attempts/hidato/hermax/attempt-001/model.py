# Hidato: fill a grid with the numbers 1..rows*cols, each once, keeping the
# given numbers, so that consecutive numbers sit in cells that touch
# horizontally, vertically or diagonally.
import functools
import operator

from hermax.model import Model


def build(instance):
    puzzle = instance["puzzle"]  # puzzle[i][j] = given number, 0 for a cell to fill in
    rows = len(puzzle)
    cols = len(puzzle[0])
    total = rows * cols  # numbers run from 1 to total

    m = Model()
    # x[i][j] = the number written in cell (i, j) (the declared output)
    x = m.int_matrix("x", rows, cols, 1, total)
    # holds[c][k - 1] = cell c = i * cols + j contains number k (one-hot form of x)
    holds = m.bool_matrix("holds", total, total)

    # every cell holds one number, and every number is in one cell
    for c in range(total):
        m &= holds.row(c).exactly_one()
        m &= holds.col(c).exactly_one()
    for i in range(rows):
        for j in range(cols):
            for k in range(1, total + 1):
                m &= (~holds[i * cols + j][k - 1] | (x[i][j] == k))

    # the given numbers stay where they are
    for i in range(rows):
        for j in range(cols):
            if puzzle[i][j] > 0:
                m &= holds[i * cols + j][puzzle[i][j] - 1]

    # The cells touching (i, j), diagonals included (and inside the grid).
    def neighbours(i, j):
        return [(i + di) * cols + (j + dj)
                for di in (-1, 0, 1) for dj in (-1, 0, 1)
                if (di, dj) != (0, 0) and 0 <= i + di < rows and 0 <= j + dj < cols]

    # Consecutive numbers touch: if a cell holds k, then one of the cells around
    # it holds k + 1 (the next number is never in the same cell, as each cell
    # holds one number). The same is stated backwards, a cell holding k + 1 has k
    # next to it; this is implied by the forward form but helps the solver.
    for i in range(rows):
        for j in range(cols):
            around = neighbours(i, j)
            for k in range(1, total):
                m &= (~holds[i * cols + j][k - 1]
                      | functools.reduce(operator.or_, [holds[n][k] for n in around]))
                m &= (~holds[i * cols + j][k]
                      | functools.reduce(operator.or_, [holds[n][k - 1] for n in around]))

    return m, {"x": x}
