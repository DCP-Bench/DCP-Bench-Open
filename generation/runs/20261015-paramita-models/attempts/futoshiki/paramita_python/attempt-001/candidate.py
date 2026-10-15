# Futoshiki: fill an n x n grid with the digits 1..n so that every row and
# every column contains each digit once, respecting the given digits and the
# "less than" signs between neighbouring cells.
# Each cell is one-hot over its digit; the grid output is the integer value.
from paramita.modelling import Bool


def build(instance):
    values = instance["values"]
    lt = instance["lt"]
    n = len(values)
    digits = range(1, n + 1)

    # v[r][c][k] = cell (r, c) holds digit k
    v = [[{k: Bool(f"v_{r}_{c}_{k}") for k in digits} for c in range(n)] for r in range(n)]
    # g[r][c] = value of cell (r, c)
    g = [[sum(k * v[r][c][k] for k in digits) for c in range(n)] for r in range(n)]

    cons = []

    # each cell holds exactly one digit
    cons += [sum(v[r][c].values()) == 1 for r in range(n) for c in range(n)]

    # each row contains each digit 1 to n exactly once
    cons += [sum(v[r][c][k] for c in range(n)) == 1 for r in range(n) for k in digits]

    # each column contains each digit 1 to n exactly once
    cons += [sum(v[r][c][k] for r in range(n)) == 1 for c in range(n) for k in digits]

    # given digits are fixed in their cells
    for r in range(n):
        for c in range(n):
            if values[r][c] > 0:
                cons.append(v[r][c][values[r][c]])

    # inequality signs: the cell on the left (or top) is less than its neighbour.
    # Positions in the instance are 1-based.
    for r1, c1, r2, c2 in lt:
        cons.append(g[r1 - 1][c1 - 1] + 1 <= g[r2 - 1][c2 - 1])

    return cons, {"grid": g}
