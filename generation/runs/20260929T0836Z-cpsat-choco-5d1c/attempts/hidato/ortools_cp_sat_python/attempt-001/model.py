# Hidato: fill the grid with the numbers 1..rows*cols, each used once, keeping
# the given numbers, so that every number k and its successor k+1 sit in
# neighbouring cells (horizontally, vertically or diagonally).
from ortools.sat.python import cp_model


def build(instance):
    puzzle = instance["puzzle"]  # given numbers; 0 marks an empty cell
    rows, cols = len(puzzle), len(puzzle[0])
    n = rows * cols

    model = cp_model.CpModel()

    # at[i][j][k] is true when cell (i, j) holds the number k + 1. With this
    # one-hot view "k and k+1 touch" becomes a plain clause per cell.
    at = [[[model.new_bool_var(f"at_{i}_{j}_{k}") for k in range(n)] for j in range(cols)] for i in range(rows)]
    # x[i][j] = the number in cell (i, j)
    x = [[model.new_int_var(1, n, f"x_{i}_{j}") for j in range(cols)] for i in range(rows)]

    for i in range(rows):
        for j in range(cols):
            # each cell holds exactly one number
            model.add_exactly_one(at[i][j])
            model.add(x[i][j] == sum((k + 1) * at[i][j][k] for k in range(n)))
    # every number is used exactly once, so together with the line above all cells differ
    for k in range(n):
        model.add_exactly_one(at[i][j][k] for i in range(rows) for j in range(cols))

    # the given numbers are fixed
    for i in range(rows):
        for j in range(cols):
            if puzzle[i][j] > 0:
                model.add(at[i][j][puzzle[i][j] - 1] == 1)

    # the successor of a number lies in one of the up to eight neighbouring cells
    for i in range(rows):
        for j in range(cols):
            near = [
                (a, b)
                for a in range(max(0, i - 1), min(rows, i + 2))
                for b in range(max(0, j - 1), min(cols, j + 2))
                if (a, b) != (i, j)
            ]
            for k in range(n - 1):
                model.add_bool_or([at[a][b][k + 1] for a, b in near]).only_enforce_if(at[i][j][k])

    return model, {"x": x}
