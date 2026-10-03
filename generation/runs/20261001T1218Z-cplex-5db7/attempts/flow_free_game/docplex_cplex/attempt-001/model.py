"""Flow Free: colour every cell of the board so that each pair of equally coloured end points
is joined by a pipe; an end point has exactly one neighbour of its colour and every other
cell exactly two.
"""
from docplex.mp.model import Model


def build(instance):
    board = instance["board"]  # board[i][j] is the colour of an end point, or 0 if empty
    M = len(board)
    N = len(board[0])
    # Colours range over 1..10, the domain the reference declares.
    max_colour = 10

    model = Model("flow_free_game")

    # B[i][j] is the colour of cell (i, j); an end point keeps its given colour.
    B = [[model.integer_var(board[i][j] if board[i][j] else 1,
                            board[i][j] if board[i][j] else max_colour, name=f"B_{i}_{j}")
          for j in range(N)] for i in range(M)]

    # same[edge] is 1 exactly when two orthogonally adjacent cells have the same colour.
    # Each such equivalence costs one binary and one constraint, which is smaller than
    # comparing one-hot colour vectors.
    same = {}
    for i in range(M):
        for j in range(N):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < M and l < N:
                    e = model.binary_var(name=f"same_{i}_{j}_{k}_{l}")
                    model.add_equivalence(e, B[i][j] == B[k][l])
                    same[(i, j), (k, l)] = e
                    same[(k, l), (i, j)] = e

    def neighbours(i, j):
        return [(k, l) for k, l in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                if 0 <= k < M and 0 <= l < N]

    for i in range(M):
        for j in range(N):
            same_neighs = model.sum(same[(i, j), c] for c in neighbours(i, j))
            if board[i][j] != 0:
                # An end point continues its pipe into exactly one neighbour.
                model.add_constraint(same_neighs == 1)
            else:
                # Any other cell lies inside a pipe: exactly two neighbours share its colour.
                model.add_constraint(same_neighs == 2)

    return model, {"B": B}
