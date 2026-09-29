# Coins grid: place coins on an n x n grid, at most one per cell and exactly c
# in every row and every column, so that the sum of the squared distances of
# the coins from the main diagonal is as small as possible.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # side of the grid
    c = instance["c"]  # coins in each row and column

    model = Model()

    # x[i][j] = 1 if there is a coin in cell (i, j); this also gives at most one coin per cell
    x = [[model.intvar(0, 1, name=f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # exactly c coins in every row
    for i in range(n):
        model.sum(x[i], "=", c).post()
    # exactly c coins in every column
    for j in range(n):
        model.sum([x[i][j] for i in range(n)], "=", c).post()

    # The cost is summed row by row: row_cost[i] = sum over the coins of row i of
    # their squared distance (i - j) ** 2 to the diagonal. Giving each row its
    # own cost variable lets Choco bound the objective row by row, which its
    # propagation handles much better than one weighted sum over all n * n cells.
    max_row_cost = c * (n - 1) ** 2
    row_costs = []
    for i in range(n):
        row_cost = model.intvar(0, max_row_cost, name=f"row_cost_{i}")
        model.scalar(x[i], [(i - j) ** 2 for j in range(n)], "=", row_cost).post()
        row_costs.append(row_cost)

    # z = the total squared distance, to be minimised
    z = model.intvar(0, n * max_row_cost, name="z")
    model.sum(row_costs, "=", z).post()

    return model, {"x": x, "z": z}, ("minimize", z)
