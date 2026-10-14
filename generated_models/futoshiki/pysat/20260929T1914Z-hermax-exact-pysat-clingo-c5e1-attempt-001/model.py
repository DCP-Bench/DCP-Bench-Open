# Futoshiki: fill an n x n grid with 1..n so that every row and column has each
# number once, some cells are given, and the listed "less than" signs between
# neighbouring cells hold.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    values = instance["values"]  # given cells; 0 means empty
    lt = instance["lt"]  # [i1, j1, i2, j2]: cell (i1, j1) must be smaller than cell (i2, j2), 1-based
    size = len(values)

    pool = IDPool()
    grid = [[Integer(f"grid_{r}_{c}", 1, size, vpool=pool) for c in range(size)] for r in range(size)]
    engine = IntegerEngine(vars=[cell for row in grid for cell in row], vpool=pool)

    # the given numbers are fixed
    for r in range(size):
        for c in range(size):
            if values[r][c] > 0:
                engine.add_linear(grid[r][c] == values[r][c])

    # every row and every column holds different numbers
    for i in range(size):
        engine.add_alldifferent(grid[i])
        engine.add_alldifferent([grid[r][i] for r in range(size)])

    # each inequality sign: the first cell is smaller than the second (the
    # coordinates in the data start at 1)
    for i1, j1, i2, j2 in lt:
        engine.add_linear(grid[i1 - 1][j1 - 1] - grid[i2 - 1][j2 - 1] <= -1)

    return engine.clausify(), {"grid": grid}
