# Magic square: fill an n x n grid with the integers 1..n^2, each used once,
# so that every row, every column and both diagonals sum to n(n^2+1)/2.
# Each cell uses a one-hot encoding over its possible values.

from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    values = range(1, n * n + 1)
    target = n * (n * n + 1) // 2    # the common line sum

    # x[i][j][v] is true when cell (i, j) holds the value v
    x = [[{v: Bool(f"x_{i}_{j}_{v}") for v in values} for j in range(n)] for i in range(n)]
    cons = []

    # each cell contains exactly one integer
    for i in range(n):
        for j in range(n):
            cons.append(sum(x[i][j].values()) == 1)

    # each integer from 1 to n^2 appears in exactly one cell
    for v in values:
        cons.append(sum(x[i][j][v] for i in range(n) for j in range(n)) == 1)

    cell = [[sum(v * x[i][j][v] for v in values) for j in range(n)] for i in range(n)]

    # every row sums to n(n^2+1)/2
    for i in range(n):
        cons.append(sum(cell[i]) == target)

    # every column sums to n(n^2+1)/2
    for j in range(n):
        cons.append(sum(cell[i][j] for i in range(n)) == target)

    # the main diagonal sums to n(n^2+1)/2
    cons.append(sum(cell[i][i] for i in range(n)) == target)

    # the anti-diagonal sums to n(n^2+1)/2
    cons.append(sum(cell[i][n - 1 - i] for i in range(n)) == target)

    return cons, {"square": cell}
