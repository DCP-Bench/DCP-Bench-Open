# Heterosquare of order n: an n x n square of distinct integers 1..n^2 such that
# the sums of the rows, the columns and the diagonals are all different.
from cvc5.pythonic import *


def build(instance):
    n = instance["n"]
    N2 = n * n

    x = [[Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    flat = [x[i][j] for i in range(n) for j in range(n)]

    constraints = []

    # The elements are distinct integers from 1 to n^2.
    # cvc5 integers are unbounded, so the bounds must be added.
    constraints += [And(c >= 1, c <= N2) for c in flat]
    if len(flat) >= 2:
        constraints.append(Distinct(flat))

    # The sums of the rows, columns and diagonals are all different.
    row_sums = [Sum(x[i]) for i in range(n)]
    col_sums = [Sum([x[i][j] for i in range(n)]) for j in range(n)]
    diag_sums = [
        Sum([x[i][i] for i in range(n)]),
        Sum([x[i][n - 1 - i] for i in range(n)]),
    ]
    all_sums = row_sums + col_sums + diag_sums
    if len(all_sums) >= 2:
        constraints.append(Distinct(all_sums))

    return constraints, {"x": x}
