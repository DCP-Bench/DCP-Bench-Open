# Sudoku: fill a 9x9 grid with the digits 1 to 9 so that each row, column and 3x3 section contains every digit once, keeping the given clues.
from pyscipopt import Model, quicksum


def build(instance):
    grid = instance["input_grid"]
    n = len(grid)  # side length, 9 for sudoku
    box = int(round(n ** 0.5))  # section side length, 3 for sudoku
    digits = range(1, n + 1)

    m = Model()

    # x[r, c, v] = 1 if cell (r, c) holds digit v
    x = {(r, c, v): m.addVar(name=f"x_{r}_{c}_{v}", vtype="B") for r in range(n) for c in range(n) for v in digits}

    # each cell holds exactly one digit
    for r in range(n):
        for c in range(n):
            m.addCons(quicksum(x[r, c, v] for v in digits) == 1)

    # each row contains every digit once
    for r in range(n):
        for v in digits:
            m.addCons(quicksum(x[r, c, v] for c in range(n)) == 1)

    # each column contains every digit once
    for c in range(n):
        for v in digits:
            m.addCons(quicksum(x[r, c, v] for r in range(n)) == 1)

    # each 3x3 section contains every digit once
    for br in range(0, n, box):
        for bc in range(0, n, box):
            for v in digits:
                m.addCons(quicksum(x[r, c, v] for r in range(br, br + box) for c in range(bc, bc + box)) == 1)

    # the given clues keep their digits (0 marks an empty cell)
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                m.addCons(x[r, c, grid[r][c]] == 1)

    # the output gives the solved digit of each cell
    solved = [[quicksum(v * x[r, c, v] for v in digits) for c in range(n)] for r in range(n)]
    return m, {"grid": solved}
