# Coins grid: place coins on an n by n grid, at most one per cell, with exactly c coins in
# every row and every column, so that the sum over all coins of the squared distance of their
# column from the main diagonal is as small as possible.
from exact import Exact


def build(instance):
    n = instance["n"]  # size of the grid
    c = instance["c"]  # coins in each row and each column

    solver = Exact()

    # x[i][j] = 1 when a coin is on row i, column j (so a cell holds at most one coin)
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 0, 1)

    # every row holds exactly c coins
    for i in range(n):
        solver.addConstraint([(1, x[i][j]) for j in range(n)], True, c, True, c)

    # every column holds exactly c coins
    for j in range(n):
        solver.addConstraint([(1, x[i][j]) for i in range(n)], True, c, True, c)

    # z is the sum, over all coins, of the squared horizontal distance (i - j)^2 from the main
    # diagonal. Its upper bound is the largest possible distance for n * c coins.
    solver.addVariable("z", 0, n * c * (n - 1) ** 2)
    distance_terms = [((i - j) ** 2, x[i][j]) for i in range(n) for j in range(n) if i != j]
    solver.addConstraint(distance_terms + [(-1, "z")], True, 0, True, 0)

    # minimise the squared distance from the diagonal
    return solver, {"x": x, "z": "z"}, ("minimize", distance_terms)
