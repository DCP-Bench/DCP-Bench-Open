# Hidato: fill a grid with the numbers 1..r*c, each once, keeping the numbers already given, so
# that consecutive numbers k and k+1 sit in cells that touch horizontally, vertically or diagonally.
from exact import Exact


def build(instance):
    puzzle = instance["puzzle"]  # puzzle[i][j] = number already in the cell, 0 for an empty cell
    r, c = len(puzzle), len(puzzle[0])
    cells = r * c
    rows, cols = range(r), range(c)

    solver = Exact()

    # holds[i][j][k-1] = 1 when cell (i, j) holds the number k. Exact has no all-different or
    # element constraint, so both "every number once" and "k+1 is next to k" use these indicators.
    holds = [[[f"cell_{i}_{j}_holds_{k}" for k in range(1, cells + 1)] for j in cols] for i in rows]
    for i in rows:
        for j in cols:
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # every cell holds exactly one number
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
    for k in range(cells):
        # every number is in exactly one cell (the numbers are all different)
        solver.addConstraint([(1, holds[i][j][k]) for i in rows for j in cols], True, 1, True, 1)

    # x[i][j] is the number in cell (i, j), from 1 to r*c
    x = [[f"x_{i}_{j}" for j in cols] for i in rows]
    for i in rows:
        for j in cols:
            solver.addVariable(x[i][j], 1, cells)
            solver.addConstraint([(k, holds[i][j][k - 1]) for k in range(1, cells + 1)] + [(-1, x[i][j])],
                                 True, 0, True, 0)

    # the numbers that are already filled in
    for i in rows:
        for j in cols:
            if puzzle[i][j] > 0:
                solver.addConstraint([(1, holds[i][j][puzzle[i][j] - 1])], True, 1, True, 1)

    # consecutive numbers touch: if cell (i, j) holds k, one of its (up to eight) neighbouring
    # cells holds k + 1
    for i in rows:
        for j in cols:
            neighbours = [(i + a, j + b) for a in (-1, 0, 1) for b in (-1, 0, 1)
                          if (a or b) and 0 <= i + a < r and 0 <= j + b < c]
            for k in range(1, cells):
                solver.addConstraint([(1, holds[ni][nj][k]) for ni, nj in neighbours]
                                     + [(-1, holds[i][j][k - 1])], True, 0)

    return solver, {"x": x}
