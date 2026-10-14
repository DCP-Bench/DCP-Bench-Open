"""Futoshiki: fill an n x n grid with the numbers 1..n so that every row and every column
holds each number once, some cells are given, and some pairs of cells carry an inequality
sign (one cell must be smaller than its neighbour).

The model reports the filled grid.
"""
import pulp


def build(instance):
    values = instance["values"]  # values[r][c] > 0 is a given number, 0 means empty
    lt = instance["lt"]  # [r1, c1, r2, c2] (1-based): the cell (r1, c1) is smaller than (r2, c2)
    n = len(values)  # grid size, also the largest number

    problem = pulp.LpProblem("futoshiki", pulp.LpMinimize)  # satisfaction: no objective

    # put[r][c][v] = 1 if the cell in row r, column c holds the number v + 1.
    # A cell holds exactly one number, and grid reads that number back.
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(n)), cat="Binary")
    grid = [[pulp.LpVariable(f"grid_{r}_{c}", 1, n, cat="Integer") for c in range(n)]
            for r in range(n)]
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(n)) == 1
            problem += grid[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(n))

    # the given numbers are fixed
    for r in range(n):
        for c in range(n):
            if values[r][c] > 0:
                problem += grid[r][c] == values[r][c]

    for v in range(n):
        # each row holds the number v + 1 once
        for r in range(n):
            problem += pulp.lpSum(put[r][c][v] for c in range(n)) == 1
        # each column holds the number v + 1 once
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for r in range(n)) == 1

    # every inequality sign holds: the first cell is smaller than the second (the numbers
    # are integers, so "smaller" is "smaller by at least 1")
    for r1, c1, r2, c2 in lt:
        problem += grid[r1 - 1][c1 - 1] + 1 <= grid[r2 - 1][c2 - 1]

    return problem, {"grid": grid}
