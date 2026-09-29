# Sudoku: complete a 9 x 9 grid so that every row, column and 3 x 3 box holds
# each of the digits 1..9 once, keeping the digits already given.
from exact import Exact


def build(instance):
    given = instance["input_grid"]  # 0 marks an empty cell
    n = len(given)
    box = 3  # side of a box

    solver = Exact()
    # grid[r][c] = the digit in cell (r, c)
    grid = [[f"grid_{r}_{c}" for c in range(n)] for r in range(n)]
    # is_[r][c][d] is 1 exactly when cell (r, c) holds digit d; the indicators
    # make "each digit once per group" a linear count
    is_ = [[{} for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            solver.addVariable(grid[r][c], 1, n)
            for d in range(1, n + 1):
                is_[r][c][d] = f"is_{r}_{c}_{d}"
                solver.addVariable(is_[r][c][d], 0, 1)
            # the cell holds exactly one digit, and grid[r][c] is that digit
            solver.addConstraint([(1, is_[r][c][d]) for d in range(1, n + 1)], True, 1, True, 1)
            solver.addConstraint([(d, is_[r][c][d]) for d in range(1, n + 1)] + [(-1, grid[r][c])],
                                 True, 0, True, 0)
            # the given digits stay
            if given[r][c] != 0:
                solver.addConstraint([(1, is_[r][c][given[r][c]])], True, 1, True, 1)

    def each_digit_once(cells):
        for d in range(1, n + 1):
            solver.addConstraint([(1, is_[r][c][d]) for r, c in cells], True, 1, True, 1)

    # each row, column and 3 x 3 box holds every digit once
    for i in range(n):
        each_digit_once([(i, c) for c in range(n)])
        each_digit_once([(r, i) for r in range(n)])
    for i in range(0, n, box):
        for j in range(0, n, box):
            each_digit_once([(r, c) for r in range(i, i + box) for c in range(j, j + box)])

    return solver, {"grid": grid}
