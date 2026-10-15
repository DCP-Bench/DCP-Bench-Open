# Magic square of size n: an n x n grid holding each integer from 1 to n^2 once,
# with every row, column and diagonal summing to n(n^2+1)/2.
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    # the cell values are the integers 1..n^2 (from the problem statement)
    values = range(1, n * n + 1)
    # the common line sum n(n^2+1)/2 is given by the problem statement
    magic = n * (n * n + 1) // 2

    # one-hot encoding: x[i][j][v] = 1 when cell (i, j) holds the integer v
    x = [[{v: Bool(f"x_{i}_{j}_{v}") for v in values} for j in range(n)] for i in range(n)]

    def cell_value(i, j):
        return sum(v * b for v, b in x[i][j].items())

    cons = []

    # each cell contains a different integer: every cell holds exactly one value
    for i in range(n):
        for j in range(n):
            cons.append(sum(x[i][j].values()) == 1)

    # each integer from 1 to n^2 is used in exactly one cell
    for v in values:
        cons.append(sum(x[i][j][v] for i in range(n) for j in range(n)) == 1)

    # the lines whose sums must be equal: rows, columns and the two diagonals
    lines = [[(i, j) for j in range(n)] for i in range(n)]
    lines += [[(i, j) for i in range(n)] for j in range(n)]
    lines.append([(i, i) for i in range(n)])
    lines.append([(i, n - 1 - i) for i in range(n)])

    # the sum of the integers in each row, column and diagonal is equal to n(n^2+1)/2
    for line in lines:
        cons.append(sum(v * b for i, j in line for v, b in x[i][j].items()) == magic)

    # the square as a list of lists of integers
    square = [[cell_value(i, j) for j in range(n)] for i in range(n)]
    return cons, {"square": square}
