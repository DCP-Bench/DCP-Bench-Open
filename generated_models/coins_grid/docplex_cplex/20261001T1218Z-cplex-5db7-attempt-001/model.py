"""Coins grid: place coins on an n by n grid, c in every row and every column, so that the sum
of the squared horizontal distances of the coins from the main diagonal is as small as possible.

A cell holds at most one coin. The squared horizontal distance of a coin in row i and column
j is (i - j) squared.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # size of the grid (n by n)
    c = instance["c"]  # coins in each row and each column

    model = Model("coins_grid")

    # x[i][j] is 1 when a coin is placed in the cell of row i and column j (at most one coin
    # per cell).
    x = [[model.binary_var(name=f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # Every row holds exactly c coins.
    for i in range(n):
        model.add_constraint(model.sum(x[i][j] for j in range(n)) == c)

    # Every column holds exactly c coins.
    for j in range(n):
        model.add_constraint(model.sum(x[i][j] for i in range(n)) == c)

    # z is the sum, over the cells with a coin, of the squared horizontal distance from the
    # main diagonal; it is the objective.
    z = model.sum(x[i][j] * (i - j) ** 2 for i in range(n) for j in range(n))
    model.minimize(z)

    return model, {"x": x, "z": z}
