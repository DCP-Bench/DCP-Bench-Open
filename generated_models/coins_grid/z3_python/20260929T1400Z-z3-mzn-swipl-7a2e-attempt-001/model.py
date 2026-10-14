# Coins grid: place coins on an n x n grid, at most one per cell and exactly c
# in every row and every column, so that the sum of the squared distances of
# the coins from the main diagonal is as small as possible.
import z3


def build(instance):
    n = instance["n"]  # side of the grid
    c = instance["c"]  # coins in each row and column

    solver = z3.Solver()

    # x[i][j] = 1 if there is a coin in cell (i, j); this also gives at most one coin per cell
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.add(x[i][j] >= 0, x[i][j] <= 1)

    # exactly c coins in every row
    for i in range(n):
        solver.add(z3.Sum(x[i]) == c)
    # exactly c coins in every column
    for j in range(n):
        solver.add(z3.Sum([x[i][j] for i in range(n)]) == c)

    # z = sum over coins of the squared horizontal distance to the diagonal,
    # (i - j) ** 2 for a coin in cell (i, j)
    z = z3.Int("z")
    solver.add(z == z3.Sum([x[i][j] * (i - j) ** 2 for i in range(n) for j in range(n)]))

    return solver, {"x": x, "z": z}, ("minimize", z)
