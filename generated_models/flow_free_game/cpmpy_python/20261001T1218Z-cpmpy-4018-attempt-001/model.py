# Flow Free: colour every cell of a board so that each colour forms one pipe between its two end
# cells. The board lists the end cells (colour 1..k) and 0 for cells that still need a colour.
import cpmpy as cp


def build(instance):
    board = instance["board"]  # board[i][j] = colour of an end cell, or 0 if the cell is empty
    rows = len(board)
    cols = len(board[0])
    n_colors = max(max(row) for row in board)  # colours are numbered 1..n_colors

    # B[i][j] = colour of the pipe through cell (i, j); every cell gets a colour
    B = cp.intvar(1, n_colors, shape=(rows, cols), name="B")

    model = cp.Model()

    for i in range(rows):
        for j in range(cols):
            # Orthogonal neighbours of the cell.
            neighbours = [(k, l) for k, l in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                          if 0 <= k < rows and 0 <= l < cols]
            # Number of neighbours that carry the same colour as this cell.
            same_colour_neighbours = cp.sum([B[i, j] == B[k, l] for k, l in neighbours])

            if board[i][j] != 0:
                # An end cell keeps its colour and joins exactly one neighbour of that colour:
                # the pipe starts here.
                model += B[i, j] == board[i][j]
                model += same_colour_neighbours == 1
            else:
                # A cell in the middle of a pipe has exactly two neighbours of its colour:
                # the pipe comes in from one and leaves through the other.
                model += same_colour_neighbours == 2

    return model, {"B": B}
