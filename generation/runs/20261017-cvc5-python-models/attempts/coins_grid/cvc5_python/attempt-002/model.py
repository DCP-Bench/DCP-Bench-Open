# Coins on a grid (cvc5 pythonic model).
# Place coins on an n by n grid so that each row and each column holds exactly c coins,
# at most one coin per cell, and the sum of the squared horizontal distances from the
# main diagonal of all cells containing a coin is as small as possible.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    c = instance["c"]

    # One 0/1 integer per cell: 1 when a coin is placed.
    x = [[cz.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    s = cz.SolverFor("QF_LIA")

    # At most one coin per cell.
    for i in range(n):
        for j in range(n):
            s.add(x[i][j] >= 0, x[i][j] <= 1)

    # In each row exactly c coins must be placed.
    for i in range(n):
        s.add(cz.Sum([x[i][j] for j in range(n)]) == c)

    # In each column exactly c coins must be placed.
    for j in range(n):
        s.add(cz.Sum([x[i][j] for i in range(n)]) == c)

    # Total coins: n rows of c coins each (follows from the row counts).
    s.add(cz.Sum([x[i][j] for i in range(n) for j in range(n)]) == n * c)

    # The sum of the quadratic horizontal distance from the main diagonal of all cells
    # containing a coin must be as small as possible. The cost of cell (i, j) is a
    # constant, so the objective is linear in the cells.
    z = cz.Int("z")
    s.add(z == cz.Sum([((i - j) ** 2) * x[i][j] for i in range(n) for j in range(n)]))

    outputs = {
        "x": x,
        "z": z,
    }
    return s, outputs, ("minimize", z)
