# Sudoku: complete a 9 x 9 grid so that every row, column and 3 x 3 box holds
# each of the digits 1..9 once, keeping the digits already given.
from pychoco.model import Model


def build(instance):
    given = instance["input_grid"]  # 0 marks an empty cell
    n = len(given)
    box = 3  # side of a box

    model = Model()

    # grid[r][c] = the digit in cell (r, c)
    grid = [[model.intvar(1, n, name=f"grid_{r}_{c}") for c in range(n)] for r in range(n)]

    # the given digits stay
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0:
                model.arithm(grid[r][c], "=", given[r][c]).post()

    # each row holds different digits
    for r in range(n):
        model.all_different(grid[r]).post()
    # each column holds different digits
    for c in range(n):
        model.all_different([grid[r][c] for r in range(n)]).post()
    # each 3 x 3 box holds different digits
    for i in range(0, n, box):
        for j in range(0, n, box):
            model.all_different([grid[r][c] for r in range(i, i + box) for c in range(j, j + box)]).post()

    return model, {"grid": grid}
