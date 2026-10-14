# Killer sudoku: fill a 9x9 grid with digits 1-9 so that rows, columns and nonets hold
# each digit once, each cage sums to its printed total, and no digit repeats within a cage.
from math import isqrt

from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]                  # grid side (9)
    cages = instance["problem"]        # list of [total, [[row, col], ...]], 1-based cells
    b_size = isqrt(n)                  # nonet side (3)
    digits = range(1, n + 1)

    m = Model()

    # b[r, c, v] = 1 if cell (r, c) holds digit v (one-hot encoding of the cell value)
    b = {(r, c, v): m.addVar(name=f"b_{r}_{c}_{v}", vtype="B")
         for r in range(n) for c in range(n) for v in digits}

    # each cell holds exactly one digit
    for r in range(n):
        for c in range(n):
            m.addCons(quicksum(b[r, c, v] for v in digits) == 1)

    # each row contains each digit exactly once
    for r in range(n):
        for v in digits:
            m.addCons(quicksum(b[r, c, v] for c in range(n)) == 1)

    # each column contains each digit exactly once
    for c in range(n):
        for v in digits:
            m.addCons(quicksum(b[r, c, v] for r in range(n)) == 1)

    # each nonet (3x3 box) contains each digit exactly once
    for br in range(0, n, b_size):
        for bc in range(0, n, b_size):
            cells = [(br + i, bc + j) for i in range(b_size) for j in range(b_size)]
            for v in digits:
                m.addCons(quicksum(b[r, c, v] for r, c in cells) == 1)

    # the cell value as an integer expression
    x = {(r, c): quicksum(v * b[r, c, v] for v in digits) for r in range(n) for c in range(n)}

    # each cage: its cells sum to the printed total
    # no digit appears more than once in a cage
    for total, cells in cages:
        cell_ids = [(r - 1, c - 1) for r, c in cells]
        m.addCons(quicksum(x[r, c] for r, c in cell_ids) == total)
        for v in digits:
            m.addCons(quicksum(b[r, c, v] for r, c in cell_ids) <= 1)

    # the solution matrix: x[r][c] is the digit in row r, column c
    grid = [[x[r, c] for c in range(n)] for r in range(n)]
    m.setObjective(0, "minimize")
    return m, {"x": grid}
