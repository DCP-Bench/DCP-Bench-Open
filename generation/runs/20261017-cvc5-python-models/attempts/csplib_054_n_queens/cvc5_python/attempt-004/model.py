# N-queens (csplib 054): place n queens on an n x n board so that no two queens
# attack each other. queens[i] is the column (1..n) of the queen in row i+1.
# Boolean board encoding: b[i][j] is true when a queen sits on row i, column j.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    b = [[cz.Bool(f"b_{i}_{j}") for j in range(n)] for i in range(n)]
    q = [cz.Int(f"q_{i}") for i in range(n)]
    constraints = []

    # Every row holds exactly one queen.
    for i in range(n):
        constraints.append(cz.Or([b[i][j] for j in range(n)]))

    # No two queens are on the same row, column or diagonal: two different
    # squares that share a row, a column or a diagonal cannot both hold a queen.
    cells = [(i, j) for i in range(n) for j in range(n)]
    for a in range(len(cells)):
        i1, j1 = cells[a]
        for c in range(a + 1, len(cells)):
            i2, j2 = cells[c]
            if i1 == i2 or j1 == j2 or i1 - j1 == i2 - j2 or i1 + j1 == i2 + j2:
                constraints.append(cz.Or(cz.Not(b[i1][j1]), cz.Not(b[i2][j2])))

    # The declared output reads each row's queen column (1-based).
    for i in range(n):
        constraints.append(q[i] >= 1)
        constraints.append(q[i] <= n)
        constraints.append(q[i] == cz.Sum([cz.If(b[i][j], j + 1, 0) for j in range(n)]))

    return constraints, {"queens": q}
