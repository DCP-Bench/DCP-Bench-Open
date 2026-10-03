"""Kakuro: put a digit from 1 to 9 into every white cell of an n x n grid so that the digits
of each entry (a run of white cells) add up to the clue of the entry and no digit is
repeated within an entry.

The model reports the grid, with 0 in the blank (black) cells.
"""
import pulp


def build(instance):
    n = instance["n"]  # grid size
    entries = instance["problem"]  # each entry is [clue, [row, col], [row, col], ...], 1-based
    blanks = instance["blanks"]  # [row, col] (1-based) of the cells that stay blank

    problem = pulp.LpProblem("kakuro", pulp.LpMinimize)  # satisfaction: no objective

    # x[r][c] = digit in the cell, 0 for a blank cell (the same domain as the reference)
    x = [[pulp.LpVariable(f"x_{r}_{c}", 0, 9, cat="Integer") for c in range(n)]
         for r in range(n)]

    # blank cells hold 0
    for r, c in blanks:
        problem += x[r - 1][c - 1] == 0

    # put[(r, c)][d - 1] = 1 if the white cell (r, c) holds the digit d. Only the cells
    # that belong to an entry get one; such a cell holds a digit from 1 to 9 (never 0), and
    # x reads the digit back.
    in_entry = {(r - 1, c - 1) for entry in entries for r, c in entry[1:]}
    put = {}
    for r, c in sorted(in_entry):
        put[(r, c)] = [pulp.LpVariable(f"put_{r}_{c}_{d}", cat="Binary") for d in range(1, 10)]
        problem += pulp.lpSum(put[(r, c)]) == 1
        problem += x[r][c] == pulp.lpSum(d * put[(r, c)][d - 1] for d in range(1, 10))

    for entry in entries:
        clue, cells = entry[0], [(r - 1, c - 1) for r, c in entry[1:]]
        # the digits of the entry add up to its clue
        problem += pulp.lpSum(x[r][c] for r, c in cells) == clue
        # no digit is repeated within the entry
        for d in range(9):
            problem += pulp.lpSum(put[cell][d] for cell in cells) <= 1

    return problem, {"x": x}
