# Coins grid: place coins on an n x n grid, at most one per cell and exactly c
# in every row and every column, so that the sum of the squared distances of
# the coins from the main diagonal is as small as possible.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]  # side of the grid
    c = instance["c"]  # coins in each row and column

    model = cp_model.CpModel()

    # x[i][j] = 1 if there is a coin in cell (i, j); this also gives at most one coin per cell
    x = [[model.new_int_var(0, 1, f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # exactly c coins in every row
    for i in range(n):
        model.add(sum(x[i]) == c)
    # exactly c coins in every column
    for j in range(n):
        model.add(sum(x[i][j] for i in range(n)) == c)

    # z = sum over coins of the squared horizontal distance to the diagonal,
    # (i - j) ** 2 for a coin in cell (i, j)
    z = model.new_int_var(0, n * n * (n - 1) ** 2, "z")
    model.add(z == sum(x[i][j] * (i - j) ** 2 for i in range(n) for j in range(n)))
    model.minimize(z)

    return model, {"x": x, "z": z}
