# Coins grid: place coins on an n x n grid, at most one per cell and exactly c
# in every row and every column, so that the sum of the squared distances of
# the coins from the main diagonal is as small as possible.
import cpmpy as cp


def build(instance):
    n = instance["n"]  # side of the grid
    c = instance["c"]  # coins in each row and column

    # x[i, j] = 1 if there is a coin in cell (i, j), 0 otherwise; the 0..1 domain also
    # gives at most one coin per cell.
    x = cp.intvar(0, 1, shape=(n, n), name="x")
    # z = the sum of the squared horizontal distances of all coins from the main diagonal.
    # Each coin adds at most (n - 1) ** 2, and there are at most n * n coins.
    z = cp.intvar(0, n * n * (n - 1) ** 2, name="z")

    model = cp.Model()

    # Exactly c coins in every row.
    for i in range(n):
        model += cp.sum(x[i, :]) == c

    # Exactly c coins in every column.
    for j in range(n):
        model += cp.sum(x[:, j]) == c

    # A coin in cell (i, j) lies |i - j| cells from the diagonal and costs that distance squared.
    model += z == cp.sum([x[i, j] * (i - j) ** 2 for i in range(n) for j in range(n)])

    # Keep the coins as close to the main diagonal as possible.
    model.minimize(z)

    return model, {"x": x, "z": z}
