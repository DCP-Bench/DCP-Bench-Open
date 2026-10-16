# Heterosquare of order n: an n*n square of distinct integers 1..n^2 whose
# row, column and diagonal sums are all different.
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    N = n * n
    values = range(1, N + 1)
    cells = [(i, j) for i in range(n) for j in range(n)]

    # One-hot encoding: x[i][j][v] is true when cell (i, j) holds the value v.
    x = [[{v: Bool(f"x_{i}_{j}_{v}") for v in values} for j in range(n)] for i in range(n)]

    cons = []

    # A heterosquare of order n is a n*n square of distinct integers from 1 to n^2:
    # every cell holds exactly one value.
    for i, j in cells:
        cons.append(sum(x[i][j][v] for v in values) == 1)
    # every value from 1 to n^2 is used by exactly one cell.
    for v in values:
        cons.append(sum(x[i][j][v] for i, j in cells) == 1)

    # Integer value of each cell, as an expression over the one-hot Bools.
    val = [[sum(v * x[i][j][v] for v in values) for j in range(n)] for i in range(n)]

    # The sums of the rows, columns and the two diagonals.
    sums = []
    for i in range(n):
        sums.append(sum(val[i][j] for j in range(n)))  # row i
    for j in range(n):
        sums.append(sum(val[i][j] for i in range(n)))  # column j
    sums.append(sum(val[k][k] for k in range(n)))  # main diagonal
    sums.append(sum(val[k][n - 1 - k] for k in range(n)))  # anti-diagonal

    # The sums of the rows, columns and diagonals are all different:
    # every pair of the 2n+2 line sums differs.
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            cons.append((sums[a] < sums[b]) | (sums[a] > sums[b]))

    outputs = {"x": [[val[i][j] for j in range(n)] for i in range(n)]}
    return cons, outputs
