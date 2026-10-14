# Flow Free: colour every cell of the board so that each pair of equal clue colours is joined
# by a pipe. A clue cell has exactly one neighbour of its colour (the pipe ends there), and
# every other cell has exactly two (the pipe passes through).
from hermax.model import Model

# Colours range over 1..10, the domain the problem's own model gives every cell.
MAX_COLOUR = 10


def build(instance):
    board = instance["board"]  # board[i][j] = clue colour of cell (i, j), 0 if it is to be filled
    rows, cols = len(board), len(board[0])
    colours = range(1, MAX_COLOUR + 1)

    m = Model()
    # B[i][j] = the colour of cell (i, j)
    B = m.int_matrix("B", rows, cols, 1, MAX_COLOUR)
    # has[i][j][c] = cell (i, j) has colour c (one-hot view of B)
    has = [[{c: m.bool(f"has_{i}_{j}_{c}") for c in colours} for j in range(cols)]
           for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            for c in colours:
                m &= (~has[i][j][c] | (B[i][j] == c))
                m &= (has[i][j][c] | ~(B[i][j] == c))

    # same[(a, b)] = neighbouring cells a and b have the same colour
    same = {}
    for i in range(rows):
        for j in range(cols):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < rows and l < cols:
                    eq = m.bool(f"same_{i}_{j}_{k}_{l}")
                    for c in colours:
                        # same colour: whatever colour one has, the other has too
                        m &= (~eq | ~has[i][j][c] | has[k][l][c])
                        # different colours: they do not share any colour
                        m &= (eq | ~has[i][j][c] | ~has[k][l][c])
                    same[(i, j), (k, l)] = eq
                    same[(k, l), (i, j)] = eq

    for i in range(rows):
        for j in range(cols):
            neighbours = [same[(i, j), (k, l)] for k, l in
                          ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                          if 0 <= k < rows and 0 <= l < cols]
            if board[i][j] != 0:
                # a clue cell keeps its colour and is the end of its pipe: exactly one
                # neighbour of the same colour
                m &= (B[i][j] == board[i][j])
                m &= (sum(neighbours) == 1)
            else:
                # any other cell lies on a pipe: exactly two neighbours of the same colour
                m &= (sum(neighbours) == 2)

    return m, {"B": B}
