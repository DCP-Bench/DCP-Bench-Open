# Futoshiki: fill an n x n grid with 1..n so that every row and column has each
# number once, some cells are given, and the listed "less than" signs between
# neighbouring cells hold.
from ortools.sat.python import cp_model


def build(instance):
    values = instance["values"]  # given cells; 0 means empty
    lt = instance["lt"]  # [i1, j1, i2, j2]: cell (i1, j1) must be smaller than cell (i2, j2), 1-based
    size = len(values)

    model = cp_model.CpModel()

    grid = [[model.new_int_var(1, size, f"grid_{r}_{c}") for c in range(size)] for r in range(size)]

    # the given numbers are fixed
    for r in range(size):
        for c in range(size):
            if values[r][c] > 0:
                model.add(grid[r][c] == values[r][c])

    # every row holds different numbers
    for r in range(size):
        model.add_all_different(grid[r])
    # every column holds different numbers
    for c in range(size):
        model.add_all_different([grid[r][c] for r in range(size)])

    # each inequality sign: the first cell is smaller than the second (the
    # coordinates in the data start at 1)
    for i1, j1, i2, j2 in lt:
        model.add(grid[i1 - 1][j1 - 1] < grid[i2 - 1][j2 - 1])

    return model, {"grid": grid}
