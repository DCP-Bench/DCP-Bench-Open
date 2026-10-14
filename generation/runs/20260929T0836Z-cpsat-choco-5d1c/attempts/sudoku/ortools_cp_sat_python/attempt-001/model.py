# Sudoku: complete a 9 x 9 grid so that every row, column and 3 x 3 box holds
# each of the digits 1..9 once, keeping the digits already given.
from ortools.sat.python import cp_model


def build(instance):
    given = instance["input_grid"]  # 0 marks an empty cell
    n = len(given)
    box = 3  # side of a box

    model = cp_model.CpModel()

    # grid[r][c] = the digit in cell (r, c)
    grid = [[model.new_int_var(1, n, f"grid_{r}_{c}") for c in range(n)] for r in range(n)]

    # the given digits stay
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0:
                model.add(grid[r][c] == given[r][c])

    # each row holds different digits
    for r in range(n):
        model.add_all_different(grid[r])
    # each column holds different digits
    for c in range(n):
        model.add_all_different([grid[r][c] for r in range(n)])
    # each 3 x 3 box holds different digits
    for i in range(0, n, box):
        for j in range(0, n, box):
            model.add_all_different([grid[r][c] for r in range(i, i + box) for c in range(j, j + box)])

    return model, {"grid": grid}
