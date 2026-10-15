# Coins on an n by n grid: place exactly c coins in every row and every column, with at most
# one coin per cell, so that the sum of the squared horizontal distances of the coins from
# the main diagonal is as small as possible.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    c = instance["c"]

    m = Model()

    # x[r, col] = 1 if a coin is placed in row r, column col (at most one coin per cell)
    x = {(r, col): m.addVar(name=f"x[{r},{col}]", vtype="B")
         for r in range(n) for col in range(n)}

    # in each row exactly c coins must be placed
    for r in range(n):
        m.addCons(quicksum(x[r, col] for col in range(n)) == c)

    # in each column exactly c coins must be placed
    for col in range(n):
        m.addCons(quicksum(x[r, col] for r in range(n)) == c)

    # z = sum of the squared horizontal distances from the main diagonal over all coins
    # (the diagonal cell of row r is column r, so the distance of cell (r, col) is col - r)
    z = m.addVar(name="z", vtype="I", lb=0)
    m.addCons(z == quicksum((col - r) ** 2 * x[r, col] for r in range(n) for col in range(n)))

    # minimise the sum of the squared distances
    m.setObjective(z, "minimize")

    return m, {"x": [[x[r, col] for col in range(n)] for r in range(n)], "z": z}
