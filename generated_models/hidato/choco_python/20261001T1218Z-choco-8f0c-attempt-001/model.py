# Hidato: fill the empty cells of a grid with the numbers 1..r*c, each used once, so that
# consecutive numbers sit in cells that touch horizontally, vertically or diagonally.
# Some numbers are already given (0 marks an empty cell).
from pychoco.model import Model


def build(instance):
    puzzle = instance["puzzle"]  # puzzle[i][j] = given number, or 0 for an empty cell
    rows, cols = len(puzzle), len(puzzle[0])
    size = rows * cols

    model = Model()

    # Cells are numbered 1..size in reading order; cell (i, j) is cell i * cols + j + 1.
    # x_flat[cell - 1] = the number written in that cell
    x_flat = [model.intvar(1, size, name=f"x_{c}") for c in range(size)]
    # where[v - 1] = the cell that holds the number v. It is the inverse of x_flat and
    # lets the "consecutive numbers touch" rule be stated as a rule on pairs of cells.
    where = [model.intvar(1, size, name=f"where_{v}") for v in range(1, size + 1)]

    # every number from 1 to rows * cols is used exactly once
    model.all_different(x_flat).post()
    model.inverse_channeling(x_flat, where, 1, 1).post()

    # the numbers that are already given
    for i in range(rows):
        for j in range(cols):
            if puzzle[i][j] > 0:
                model.arithm(x_flat[i * cols + j], "=", puzzle[i][j]).post()

    # two different cells touch if they differ by at most one row and one column
    touching_cells = []
    for i in range(rows):
        for j in range(cols):
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    if (a, b) != (0, 0) and 0 <= i + a < rows and 0 <= j + b < cols:
                        touching_cells.append([i * cols + j + 1, (i + a) * cols + (j + b) + 1])

    # the cell of number v + 1 touches the cell of number v
    for v in range(size - 1):
        model.table([where[v], where[v + 1]], touching_cells).post()

    x = [[x_flat[i * cols + j] for j in range(cols)] for i in range(rows)]
    return model, {"x": x}
