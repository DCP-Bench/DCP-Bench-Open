# Session 1 magic square: an n x n grid where each cell holds a different integer
# from 1 to n^2, and the sum of the integers in each row, column and diagonal is
# equal to n(n^2 + 1)/2. The output is the grid as a list of lists.
# Encoding: one Boolean per (cell, value) pair, so that "different integers" becomes
# exactly-one constraints on Booleans rather than disequalities over integers.
import cvc5.pythonic as cz


def exactly_one(lits):
    # one literal is forced true; two or more are forbidden pairwise
    constraints = []
    if len(lits) == 1:
        constraints.append(lits[0])
        return constraints
    constraints.append(cz.Or(lits))
    for a in range(len(lits)):
        for b in range(a + 1, len(lits)):
            constraints.append(cz.Or(cz.Not(lits[a]), cz.Not(lits[b])))
    return constraints


def build(instance):
    n = instance["n"]
    m = n * n
    target = n * (n * n + 1) // 2

    # x[i][j][v] is true when cell (i, j) holds the integer v + 1
    x = [[[cz.Bool(f"x_{i}_{j}_{v}") for v in range(m)] for j in range(n)] for i in range(n)]

    constraints = []

    # each cell contains a different integer from 1 to n^2: exactly one value per cell
    for i in range(n):
        for j in range(n):
            constraints += exactly_one(x[i][j])

    # each integer from 1 to n^2 is in exactly one cell
    cells = [(i, j) for i in range(n) for j in range(n)]
    for v in range(m):
        constraints += exactly_one([x[i][j][v] for (i, j) in cells])

    # the integer in each cell
    values = [[cz.Int(f"s_{i}_{j}") for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            constraints.append(values[i][j] == sum(cz.If(x[i][j][v], v + 1, 0) for v in range(m)))

    # the sum of the integers in each row is n(n^2 + 1)/2
    for i in range(n):
        constraints.append(sum(values[i][j] for j in range(n)) == target)

    # the sum of the integers in each column is n(n^2 + 1)/2
    for j in range(n):
        constraints.append(sum(values[i][j] for i in range(n)) == target)

    # the sum of the integers in each diagonal is n(n^2 + 1)/2
    constraints.append(sum(values[i][i] for i in range(n)) == target)
    constraints.append(sum(values[i][n - 1 - i] for i in range(n)) == target)

    return constraints, {"square": values}
