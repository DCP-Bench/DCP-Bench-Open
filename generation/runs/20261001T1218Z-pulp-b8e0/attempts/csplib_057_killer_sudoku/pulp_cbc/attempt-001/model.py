"""Killer sudoku: fill an n x n grid with the numbers 1..n so that every row, column and
box holds each number once, and for every cage (a group of cells with a small number
printed in its corner) the numbers in the cage add up to that number and are all different.

The model reports the filled grid.
"""
import math

import pulp


def build(instance):
    n = instance["n"]  # grid size
    cages = instance["problem"]  # each cage is [sum, [[row, col], ...]] with 1-based cells
    box = math.isqrt(n)  # boxes are box x box

    problem = pulp.LpProblem("killer_sudoku", pulp.LpMinimize)  # satisfaction: no objective

    # put[r][c][v] = 1 if the cell in row r, column c holds the number v + 1.
    # The cell holds exactly one number, and x reads that number back.
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(n)), cat="Binary")
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, n, cat="Integer") for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(n)) == 1
            problem += x[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(n))

    for v in range(n):
        # each row holds the number v + 1 once
        for r in range(n):
            problem += pulp.lpSum(put[r][c][v] for c in range(n)) == 1
        # each column holds the number v + 1 once
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for r in range(n)) == 1
        # each box holds the number v + 1 once
        for top in range(0, n, box):
            for left in range(0, n, box):
                problem += pulp.lpSum(put[r][c][v]
                                      for r in range(top, top + box)
                                      for c in range(left, left + box)) == 1

    # cages: the numbers in a cage add up to its sum and are all different
    for total, cells in cages:
        cells = [(r - 1, c - 1) for r, c in cells]  # to 0-based
        problem += pulp.lpSum(x[r][c] for r, c in cells) == total
        for v in range(n):
            problem += pulp.lpSum(put[r][c][v] for r, c in cells) <= 1

    return problem, {"x": x}
