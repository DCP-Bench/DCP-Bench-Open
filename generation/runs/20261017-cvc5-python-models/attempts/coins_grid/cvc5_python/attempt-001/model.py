# Coins on a grid (cvc5 pythonic model).
# Place coins on an n by n grid so that each row and each column holds exactly c coins,
# at most one coin per cell, and the sum of the squared horizontal distances from the
# main diagonal of all cells containing a coin is as small as possible.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    c = instance["c"]

    # A coin is placed (True) or not (False) in each cell.
    x = [[cz.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    constraints = []

    # In each row exactly c coins must be placed.
    for i in range(n):
        constraints.append(cz.Sum([cz.If(x[i][j], 1, 0) for j in range(n)]) == c)

    # In each column exactly c coins must be placed.
    for j in range(n):
        constraints.append(cz.Sum([cz.If(x[i][j], 1, 0) for i in range(n)]) == c)

    # The sum of the quadratic horizontal distance from the main diagonal of all cells
    # containing a coin must be as small as possible.
    z = cz.Sum([cz.If(x[i][j], (i - j) ** 2, 0) for i in range(n) for j in range(n)])

    outputs = {
        "x": x,
        "z": z,
    }
    return constraints, outputs, ("minimize", z)
