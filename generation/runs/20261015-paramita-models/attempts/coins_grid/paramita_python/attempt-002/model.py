# Coins on a grid: place coins on an n by n grid, c per row and c per column,
# at most one coin per cell, minimising the sum of the squared horizontal
# distances of the coins from the main diagonal.
from paramita.modelling import Bool


def build(instance):
    n, c = instance["n"], instance["c"]
    cons = []

    # x[i][j] is true when a coin is placed in row i, column j.
    # Each cell is one Bool, so it holds at most one coin.
    x = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # In each row exactly c coins must be placed.
    for i in range(n):
        cons.append(sum(x[i]) == c)

    # In each column exactly c coins must be placed.
    for j in range(n):
        cons.append(sum(x[i][j] for i in range(n)) == c)

    # The sum of the quadratic horizontal distance from the main diagonal of all
    # cells containing a coin must be as small as possible.
    # A coin in cell (i, j) is at horizontal distance |i - j| from the diagonal
    # cell of its row, so its squared distance is (i - j)^2.
    # (cells on the diagonal have distance 0 and are left out of the sum)
    z = sum((i - j) ** 2 * x[i][j] for i in range(n) for j in range(n) if i != j)

    # the brief declares x as integers (0 or 1), so each cell is read as an integer
    return cons, {"x": [[1 * x[i][j] for j in range(n)] for i in range(n)], "z": z}, ("minimize", z)
