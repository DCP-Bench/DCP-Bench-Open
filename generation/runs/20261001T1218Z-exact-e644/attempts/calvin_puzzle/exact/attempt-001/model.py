# Calvin puzzle: fill an n x n grid with the numbers 1..n^2, each once, so that every number k is
# followed by k + 1 exactly three squares away horizontally or vertically, or exactly two squares
# away on both axes (diagonally).
from exact import Exact


def build(instance):
    n = instance["n"]  # side of the grid
    cells = n * n

    # moves from one number to the next: (row step, column step). Three squares along a row or a
    # column, or two squares along both (these moves are part of the problem statement).
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    def reachable(i, j):
        # cells that a number placed at (i, j) can be followed by
        return [(i + a) * n + (j + b) for a, b in moves
                if 0 <= i + a < n and 0 <= j + b < n]

    solver = Exact()

    # x[i][j] = the number written in cell (i, j), between 1 and n^2
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 1, cells)

    # at[k][c] = 1 when number k (1-based) is in cell c = i * n + j. The "next number" rule talks
    # about where a given number is, so each number gets one 0/1 variable per cell.
    at = [[f"at_{k}_{c}" for c in range(cells)] for k in range(cells + 1)]
    for k in range(1, cells + 1):
        for c in range(cells):
            solver.addVariable(at[k][c], 0, 1)

    # all different: every number is in exactly one cell, and every cell holds exactly one number
    for k in range(1, cells + 1):
        solver.addConstraint([(1, at[k][c]) for c in range(cells)], True, 1, True, 1)
    for c in range(cells):
        solver.addConstraint([(1, at[k][c]) for k in range(1, cells + 1)], True, 1, True, 1)
        # the cell's value x[i][j] is the number placed there
        i, j = divmod(c, n)
        solver.addConstraint([(k, at[k][c]) for k in range(1, cells + 1)] + [(-1, x[i][j])],
                             True, 0, True, 0)

    # valid moves: if number k is in a cell, number k + 1 is in one of the cells a move away
    # (k + 1 has to be in a valid cell, so it is required to be reachable from its predecessor
    # as well)
    for k in range(1, cells):
        for c in range(cells):
            i, j = divmod(c, n)
            ahead = reachable(i, j)
            solver.addConstraint([(1, at[k][c])] + [(-1, at[k + 1][d]) for d in ahead],
                                 False, 0, True, 0)
            # the cells that can follow cell c are exactly the cells that can precede it
            solver.addConstraint([(1, at[k + 1][c])] + [(-1, at[k][d]) for d in ahead],
                                 False, 0, True, 0)

    return solver, {"x": x}
