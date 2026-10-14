# Flow Free: colour every cell of the board so that each colour forms one pipe
# joining its two given end cells, the pipes do not cross or overlap, and the
# whole board is covered. A pipe is a chain of orthogonally adjacent cells of
# one colour.
from ortools.sat.python import cp_model


def build(instance):
    board = instance["board"]  # colour of each end cell, 0 for a cell to fill
    rows, cols = len(board), len(board[0])
    n_colors = max(max(row) for row in board)  # colours are numbered 1..n_colors

    model = cp_model.CpModel()

    # B[i][j] = colour of cell (i, j)
    B = [[model.new_int_var(1, n_colors, f"B_{i}_{j}") for j in range(cols)] for i in range(rows)]

    # same[(cell, neighbour)] is true when two adjacent cells have the same colour
    same = {}
    incident = {(i, j): [] for i in range(rows) for j in range(cols)}
    for i in range(rows):
        for j in range(cols):
            for a, b in ((i + 1, j), (i, j + 1)):
                if a < rows and b < cols:
                    lit = model.new_bool_var(f"same_{i}_{j}_{a}_{b}")
                    model.add(B[i][j] == B[a][b]).only_enforce_if(lit)
                    model.add(B[i][j] != B[a][b]).only_enforce_if(lit.negated())
                    incident[(i, j)].append(lit)
                    incident[(a, b)].append(lit)

    for i in range(rows):
        for j in range(cols):
            same_neighbours = sum(incident[(i, j)])
            if board[i][j] != 0:
                # an end cell has its given colour and joins exactly one neighbour of that colour
                model.add(B[i][j] == board[i][j])
                model.add(same_neighbours == 1)
            else:
                # a cell in the middle of a pipe joins exactly two neighbours of its colour
                model.add(same_neighbours == 2)

    return model, {"B": B}
