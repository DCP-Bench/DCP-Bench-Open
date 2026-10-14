"""Magic square: fill an n x n grid with the different integers 1..n^2 so that every row,
every column and both diagonals add up to the same sum, n * (n^2 + 1) / 2.

The model reports the square.
"""
import itertools

import pulp


def build(instance):
    n = instance["n"]  # size of the square
    cells = n * n  # the entries are the numbers 1..cells
    magic_sum = n * (n ** 2 + 1) // 2  # sum of each row, column and diagonal

    problem = pulp.LpProblem("magic_square", pulp.LpMinimize)  # satisfaction: no objective

    # square[r][c] = the number in the cell
    square = [[pulp.LpVariable(f"square_{r}_{c}", 1, cells, cat="Integer") for c in range(n)]
              for r in range(n)]
    positions = [(r, c) for r in range(n) for c in range(n)]

    # All numbers are different: for two cells, one number is smaller than the other.
    # smaller[(p, q)] = 1 if the number in p is below the number in q. Big-M: two numbers differ
    # by at most cells - 1, so a slack of cells always suffices. (Pairwise orderings rather than
    # a number-per-cell assignment: this keeps the program small, about n^4 / 2 binaries.)
    for p, q in itertools.combinations(positions, 2):
        a, b = square[p[0]][p[1]], square[q[0]][q[1]]
        smaller = pulp.LpVariable(f"smaller_{p[0]}_{p[1]}_{q[0]}_{q[1]}", cat="Binary")
        problem += a <= b - 1 + cells * (1 - smaller)
        problem += a >= b + 1 - cells * smaller

    # every row adds up to the magic sum
    for r in range(n):
        problem += pulp.lpSum(square[r][c] for c in range(n)) == magic_sum

    # every column adds up to the magic sum
    for c in range(n):
        problem += pulp.lpSum(square[r][c] for r in range(n)) == magic_sum

    # the main diagonal adds up to the magic sum
    problem += pulp.lpSum(square[i][i] for i in range(n)) == magic_sum

    # the other diagonal adds up to the magic sum
    problem += pulp.lpSum(square[i][n - 1 - i] for i in range(n)) == magic_sum

    return problem, {"square": square}
