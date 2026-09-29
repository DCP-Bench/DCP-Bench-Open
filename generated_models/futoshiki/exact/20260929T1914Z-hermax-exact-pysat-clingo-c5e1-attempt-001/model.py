# Futoshiki: fill an n x n grid with 1..n so that every row and column has each
# number once, some cells are given, and the listed "less than" signs between
# neighbouring cells hold.
from exact import Exact


def build(instance):
    values = instance["values"]  # given cells; 0 means empty
    lt = instance["lt"]  # [i1, j1, i2, j2]: cell (i1, j1) must be smaller than cell (i2, j2), 1-based
    size = len(values)

    solver = Exact()
    grid = [[f"grid_{r}_{c}" for c in range(size)] for r in range(size)]
    # is_[r][c][d] is 1 exactly when cell (r, c) holds d; they make "different
    # numbers in a line" a count of at most one per number
    is_ = [[{} for _ in range(size)] for _ in range(size)]
    for r in range(size):
        for c in range(size):
            solver.addVariable(grid[r][c], 1, size)
            for d in range(1, size + 1):
                is_[r][c][d] = f"is_{r}_{c}_{d}"
                solver.addVariable(is_[r][c][d], 0, 1)
            solver.addConstraint([(1, is_[r][c][d]) for d in range(1, size + 1)], True, 1, True, 1)
            solver.addConstraint([(d, is_[r][c][d]) for d in range(1, size + 1)] + [(-1, grid[r][c])],
                                 True, 0, True, 0)
            # the given numbers are fixed
            if values[r][c] > 0:
                solver.addConstraint([(1, is_[r][c][values[r][c]])], True, 1, True, 1)

    # every row and every column holds each number once
    for d in range(1, size + 1):
        for i in range(size):
            solver.addConstraint([(1, is_[i][c][d]) for c in range(size)], True, 1, True, 1)
            solver.addConstraint([(1, is_[r][i][d]) for r in range(size)], True, 1, True, 1)

    # each inequality sign: the first cell is smaller than the second, that is,
    # first - second <= -1 (the coordinates in the data start at 1)
    for i1, j1, i2, j2 in lt:
        solver.addConstraint([(1, grid[i1 - 1][j1 - 1]), (-1, grid[i2 - 1][j2 - 1])], False, 0, True, -1)

    return solver, {"grid": grid}
