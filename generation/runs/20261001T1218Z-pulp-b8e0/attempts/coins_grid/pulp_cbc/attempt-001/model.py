"""Coins grid: place coins on an n x n grid, at most one per cell, with exactly c
coins in every row and every column, so that the sum of the squared horizontal
distances of the coins from the main diagonal is as small as possible.

A coin in row i and column j is |i - j| cells from the diagonal, so it costs
(i - j)^2. The model outputs the placement x and the total cost z.
"""
import pulp


def build(instance):
    n = instance["n"]  # grid size
    c = instance["c"]  # coins in each row and each column

    problem = pulp.LpProblem("coins_grid", pulp.LpMinimize)

    # x[i][j] = 1 if there is a coin in row i, column j (at most one coin per cell
    # is the 0/1 domain) (declared output)
    x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(n)] for i in range(n)]

    # z = sum of the squared distances to the diagonal of the cells holding a coin
    # (declared output). A coin is at most n-1 cells away, and there are n*c coins,
    # so z is at most n * c * (n-1)^2.
    z = pulp.LpVariable("z", 0, n * c * (n - 1) ** 2, cat="Integer")
    cost = pulp.lpSum((i - j) ** 2 * x[i][j] for i in range(n) for j in range(n))
    problem += z == cost

    # objective: minimise the squared distance to the diagonal
    problem += cost

    # every row holds exactly c coins
    for i in range(n):
        problem += pulp.lpSum(x[i]) == c

    # every column holds exactly c coins
    for j in range(n):
        problem += pulp.lpSum(x[i][j] for i in range(n)) == c

    return problem, {"x": x, "z": z}
