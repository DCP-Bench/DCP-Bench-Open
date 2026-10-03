"""Magic square: fill an n x n grid with the different integers 1..n^2 so that every row,
every column and both diagonals add up to the same sum, n * (n^2 + 1) / 2.

The model reports the square.
"""
import pulp


def build(instance):
    n = instance["n"]  # size of the square
    cells = n * n  # the entries are the numbers 1..cells
    magic_sum = n * (n ** 2 + 1) // 2  # sum of each row, column and diagonal

    problem = pulp.LpProblem("magic_square", pulp.LpMinimize)  # satisfaction: no objective

    # put[r][c][v] = 1 if the cell in row r, column c holds the number v + 1. All the entries
    # are different and there are as many numbers as cells, so every number is used exactly
    # once. square reads the number of a cell back.
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(cells)), cat="Binary")
    square = [[pulp.LpVariable(f"square_{r}_{c}", 1, cells, cat="Integer") for c in range(n)]
              for r in range(n)]
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(cells)) == 1
            problem += square[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(cells))
    for v in range(cells):
        problem += pulp.lpSum(put[r][c][v] for r in range(n) for c in range(n)) == 1

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
