# Coins grid: place coins on an n by n grid, at most one per cell, with exactly
# c coins in every row and every column, so that the sum of the squared
# horizontal distances of the coins from the main diagonal is as small as possible.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # side of the grid
    c = instance["c"]  # coins in each row and each column

    m = Model()
    # x[i][j] = 1 if there is a coin in cell (i, j), otherwise 0 (at most one per cell)
    x = m.int_matrix("x", n, n, 0, 1)
    # coin[i][j] is the literal "there is a coin in cell (i, j)"
    coin = [[x[i][j] >= 1 for j in range(n)] for i in range(n)]

    for i in range(n):
        # every row holds exactly c coins
        m &= (sum(x[i][j] for j in range(n)) == c)
        # every column holds exactly c coins
        m &= (sum(x[j][i] for j in range(n)) == c)

    # A coin in cell (i, j) is (i - j)^2 away from the diagonal. Minimise the sum:
    # each coin pays its distance (a soft clause pays when its literal is false,
    # so the literal is the negation of "there is a coin").
    for i in range(n):
        for j in range(n):
            if i != j:
                m.obj[(i - j) ** 2] += ~coin[i][j]

    # z is a declared output, so it is the same sum as an integer. It is built
    # from scaled cells (hermax adds them up in narrow partial sums) rather than
    # tied to the objective with one wide equality, which is far more expensive.
    z = m.sum_var([m.scale(x[i][j], (i - j) ** 2)
                   for i in range(n) for j in range(n) if i != j])

    return m, {"x": x, "z": z}
