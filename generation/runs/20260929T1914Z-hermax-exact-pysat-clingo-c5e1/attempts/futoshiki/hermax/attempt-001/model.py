# Futoshiki: fill an n x n grid with 1..n so that every row and column has each
# number once, some cells are given, and the listed "less than" signs between
# neighbouring cells hold.
from hermax.model import Model


def build(instance):
    values = instance["values"]  # given cells; 0 means empty
    lt = instance["lt"]  # [i1, j1, i2, j2]: cell (i1, j1) must be smaller than cell (i2, j2), 1-based
    size = len(values)

    m = Model()
    grid = m.int_matrix("grid", size, size, 1, size)

    # the given numbers are fixed
    for r in range(size):
        for c in range(size):
            if values[r][c] > 0:
                m &= (grid[r][c] == values[r][c])

    # every row and every column holds different numbers
    for i in range(size):
        m &= grid.row(i).all_different()
        m &= grid.col(i).all_different()

    # each inequality sign: the first cell is smaller than the second (the
    # coordinates in the data start at 1)
    for i1, j1, i2, j2 in lt:
        m &= (grid[i1 - 1][j1 - 1] < grid[i2 - 1][j2 - 1])

    return m, {"grid": grid}
