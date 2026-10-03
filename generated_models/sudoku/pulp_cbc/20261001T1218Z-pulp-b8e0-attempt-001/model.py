"""Sudoku: fill a 9 x 9 grid with the digits 1 to 9 so that every row, every column and every
3 x 3 box holds each digit once. Some cells are given.

The model reports the solved grid.
"""
import math

import pulp


def build(instance):
    given = instance["input_grid"]  # given[r][c] > 0 is a given digit, 0 (the empty value) is empty
    n = len(given)  # 9
    box = math.isqrt(n)  # boxes are 3 x 3

    problem = pulp.LpProblem("sudoku", pulp.LpMinimize)  # satisfaction: no objective

    # put[r][c][v] = 1 if the cell in row r, column c holds the digit v + 1. A cell holds
    # exactly one digit, and grid reads that digit back.
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(n)), cat="Binary")
    grid = [[pulp.LpVariable(f"grid_{r}_{c}", 1, n, cat="Integer") for c in range(n)]
            for r in range(n)]
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(n)) == 1
            problem += grid[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(n))

    # the given digits are fixed
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0:
                problem += grid[r][c] == given[r][c]

    for v in range(n):
        # each row holds the digit v + 1 once
        for r in range(n):
            problem += pulp.lpSum(put[r][c][v] for c in range(n)) == 1
        # each column holds the digit v + 1 once
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for r in range(n)) == 1
        # each box holds the digit v + 1 once
        for top in range(0, n, box):
            for left in range(0, n, box):
                problem += pulp.lpSum(put[r][c][v]
                                      for r in range(top, top + box)
                                      for c in range(left, left + box)) == 1

    return problem, {"grid": grid}
