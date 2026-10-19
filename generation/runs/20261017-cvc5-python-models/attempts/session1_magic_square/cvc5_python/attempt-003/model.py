# Session 1 magic square: an n x n grid where each cell holds a different integer
# from 1 to n^2, and the sum of the integers in each row, column and diagonal is
# equal to n(n^2 + 1)/2. The output is the grid as a list of lists.
# Encoding: one 0/1 integer per (cell, value) pair. Each cell holds exactly one value,
# each value sits in exactly one cell, and the line sums are linear in the 0/1 variables.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = n * n
    target = n * (n * n + 1) // 2

    # x[i][j][v] is 1 when cell (i, j) holds the integer v + 1, otherwise 0
    x = [[[cz.Int(f"x_{i}_{j}_{v}") for v in range(m)] for j in range(n)] for i in range(n)]
    cells = [(i, j) for i in range(n) for j in range(n)]

    constraints = []

    # 0/1 bounds on every variable
    for i, j in cells:
        for v in range(m):
            constraints.append(x[i][j][v] >= 0)
            constraints.append(x[i][j][v] <= 1)

    # each cell contains a different integer from 1 to n^2: exactly one value per cell
    for i, j in cells:
        constraints.append(sum(x[i][j][v] for v in range(m)) == 1)

    # each integer from 1 to n^2 is in exactly one cell
    for v in range(m):
        constraints.append(sum(x[i][j][v] for (i, j) in cells) == 1)

    def value(i, j):
        return sum((v + 1) * x[i][j][v] for v in range(m))

    # the sum of the integers in each row is n(n^2 + 1)/2
    for i in range(n):
        constraints.append(sum(value(i, j) for j in range(n)) == target)

    # the sum of the integers in each column is n(n^2 + 1)/2
    for j in range(n):
        constraints.append(sum(value(i, j) for i in range(n)) == target)

    # the sum of the integers in each diagonal is n(n^2 + 1)/2
    constraints.append(sum(value(i, i) for i in range(n)) == target)
    constraints.append(sum(value(i, n - 1 - i) for i in range(n)) == target)

    return constraints, {"square": [[value(i, j) for j in range(n)] for i in range(n)]}
