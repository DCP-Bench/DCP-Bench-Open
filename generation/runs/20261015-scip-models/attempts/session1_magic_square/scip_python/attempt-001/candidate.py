# Magic square: fill an n x n grid with the integers 1..n^2, each used once, so that every row, column and both diagonals have the same sum.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    N = n * n
    # each row, column and diagonal sums to n(n^2+1)/2
    line_sum = n * (N + 1) // 2

    m = Model()
    # b[i, j, v] = 1 if cell (i, j) holds the value v (values 1..n^2)
    b = {(i, j, v): m.addVar(name=f"b_{i}_{j}_{v}", vtype="B")
         for i in range(n) for j in range(n) for v in range(1, N + 1)}

    # each cell holds exactly one value
    for i in range(n):
        for j in range(n):
            m.addCons(quicksum(b[i, j, v] for v in range(1, N + 1)) == 1)

    # each value is used in exactly one cell (all different)
    for v in range(1, N + 1):
        m.addCons(quicksum(b[i, j, v] for i in range(n) for j in range(n)) == 1)

    # cell values as expressions of the one-hot choice
    x = [[quicksum(v * b[i, j, v] for v in range(1, N + 1)) for j in range(n)]
         for i in range(n)]

    # every row sums to the magic constant
    for i in range(n):
        m.addCons(quicksum(x[i][j] for j in range(n)) == line_sum)

    # every column sums to the magic constant
    for j in range(n):
        m.addCons(quicksum(x[i][j] for i in range(n)) == line_sum)

    # the main diagonal sums to the magic constant
    m.addCons(quicksum(x[i][i] for i in range(n)) == line_sum)

    # the anti-diagonal sums to the magic constant
    m.addCons(quicksum(x[i][n - 1 - i] for i in range(n)) == line_sum)

    return m, {"square": x}
