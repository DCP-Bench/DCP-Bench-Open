# Heterosquare of order n: an n*n square of distinct integers 1..n^2 whose
# row, column and diagonal sums are all different.
from paramita.modelling import Bool, If, Or


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

    # The lines of the square: the n rows, the n columns and the two diagonals.
    lines = []
    for i in range(n):
        lines.append([(i, j) for j in range(n)])  # row i
    for j in range(n):
        lines.append([(i, j) for i in range(n)])  # column j
    lines.append([(k, k) for k in range(n)])  # main diagonal
    lines.append([(k, n - 1 - k) for k in range(n)])  # anti-diagonal

    # The sum of a line of n distinct values from 1 to n^2 lies between lo and hi.
    lo = n * (n + 1) // 2
    hi = n * N - n * (n - 1) // 2
    width = hi - lo

    # Unary (order) encoding of each line sum: u[a][k] is true when the sum of
    # line a is at least lo + k. Each line sum is tied to its unary bits.
    unary = []
    for a, line in enumerate(lines):
        u = [Bool(f"sum_{a}_ge_{lo + k}") for k in range(1, width + 1)]
        # the bits are monotone: if the sum is at least k + 1 it is at least k
        for k in range(width - 1):
            cons.append(If(u[k + 1], u[k]))
        # the line sum, from the values in its cells, equals lo plus the number of true bits
        cons.append(sum(val[i][j] for i, j in line) == lo + sum(u))
        unary.append(u)

    # The sums of the rows, columns and diagonals are all different: for every
    # pair of lines, the two unary encodings differ at some position.
    for a in range(len(lines)):
        for b in range(a + 1, len(lines)):
            differ = []
            for k in range(width):
                d = Bool(f"differ_{a}_{b}_{k}")
                ua, ub = unary[a][k], unary[b][k]
                cons.append(If(d, (ua & ~ub) | (~ua & ub)))
                differ.append(d)
            cons.append(Or(differ))

    outputs = {"x": [[val[i][j] for j in range(n)] for i in range(n)]}
    return cons, outputs
