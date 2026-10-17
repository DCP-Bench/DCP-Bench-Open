# Futoshiki: place the digits 1 to n on an n x n grid (n from the instance) so that
# each row and each column contains each digit exactly once. Some cells are given
# (nonzero entries of "values", 0 means empty) and must keep their digit. Inequality
# pairs in "lt" are [r1, c1, r2, c2] with 1-based coordinates: the digit in cell
# (r1, c1) must be lower than the digit in cell (r2, c2).
import cvc5.pythonic as cz


def build(instance):
    values = instance["values"]
    lt = instance["lt"]
    n = len(values)

    grid = [[cz.Int(f"g_{r}_{c}") for c in range(n)] for r in range(n)]
    cons = []

    # Each cell holds a digit from 1 to n.
    for r in range(n):
        for c in range(n):
            cons.append(grid[r][c] >= 1)
            cons.append(grid[r][c] <= n)

    # Each row and each column contains each digit once.
    for r in range(n):
        cons.append(cz.Distinct(grid[r]))
    for c in range(n):
        cons.append(cz.Distinct([grid[r][c] for r in range(n)]))

    # Some digits may be given at the start.
    for r in range(n):
        for c in range(n):
            if values[r][c] != 0:
                cons.append(grid[r][c] == values[r][c])

    # Inequality constraints are specified between some of the squares, such that
    # one must be lower than its neighbour.
    for r1, c1, r2, c2 in lt:
        cons.append(grid[r1 - 1][c1 - 1] < grid[r2 - 1][c2 - 1])

    return cons, {"grid": grid}
