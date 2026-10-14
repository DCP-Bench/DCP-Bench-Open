# Futoshiki: fill an n-by-n grid with 1..n so that every row and column holds each number
# once, some cells are given, and a set of "less than" signs between neighbouring cells hold.
import cpmpy as cp


def build(instance):
    values = instance["values"]     # values[i][j] is the given number in row i, column j; 0 means empty
    lt = instance["lt"]             # each [i1, j1, i2, j2] (1-based) requires cell (i1, j1) < cell (i2, j2)
    size = len(values)

    grid = cp.intvar(1, size, shape=(size, size), name="grid")

    model = cp.Model()

    # The numbers given at the start are fixed.
    for i in range(size):
        for j in range(size):
            if values[i][j] > 0:
                model += grid[i, j] == values[i][j]

    # Every row contains each number once.
    for i in range(size):
        model += cp.AllDifferent(grid[i, :])

    # Every column contains each number once.
    for j in range(size):
        model += cp.AllDifferent(grid[:, j])

    # Every inequality sign holds: the first cell is smaller than the second (cells are 1-based in the data).
    for i1, j1, i2, j2 in lt:
        model += grid[i1 - 1, j1 - 1] < grid[i2 - 1, j2 - 1]

    return model, {"grid": grid}
