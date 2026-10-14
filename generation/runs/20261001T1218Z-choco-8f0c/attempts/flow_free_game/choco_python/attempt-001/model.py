# Flow Free: colour every cell of the board so that each pair of same-coloured endpoints is joined by
# a pipe of that colour; pipes never cross, overlap or branch.
from pychoco.model import Model


def build(instance):
    board = instance["board"]  # board[i][j] = colour of an endpoint, or 0 for a cell to fill
    rows, cols = len(board), len(board[0])
    # The statement asks for each cell's colour as one of the board's colours.
    n_colours = max(max(row) for row in board)

    model = Model()

    # B[i][j] = the colour of cell (i, j)
    B = [[model.intvar(1, n_colours, name=f"B_{i}_{j}") for j in range(cols)] for i in range(rows)]

    # same[(a, b)] is true when the orthogonally adjacent cells a and b have the same colour
    same = {}
    for i in range(rows):
        for j in range(cols):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < rows and l < cols:
                    same[(i, j), (k, l)] = model.arithm(B[i][j], "=", B[k][l]).reify()

    def same_neighbours(i, j):
        return [b for (a, c), b in same.items() if (i, j) in (a, c)]

    for i in range(rows):
        for j in range(cols):
            if board[i][j] != 0:
                # An endpoint keeps its colour and has exactly one neighbour of that colour (the
                # pipe leaves it in one direction).
                model.arithm(B[i][j], "=", board[i][j]).post()
                model.sum(same_neighbours(i, j), "=", 1).post()
            else:
                # Any other cell lies on a pipe, which enters and leaves it: exactly two
                # neighbours share its colour.
                model.sum(same_neighbours(i, j), "=", 2).post()

    return model, {"B": B}
