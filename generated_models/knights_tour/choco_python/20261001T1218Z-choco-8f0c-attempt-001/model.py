# Knight's tour: number the squares of an n x n chessboard 0..n*n-1 so that the knight can
# go from each square to the next number by a knight's move, visiting every square once.
# The tour does not have to return to the start.
from pychoco.model import Model

# the eight knight moves as (row change, column change)
KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def build(instance):
    n = instance["n"]  # side of the board
    size = n * n

    model = Model()

    # Square (i, j) is square i * n + j.
    # x_flat[square] = the move number of the knight on that square
    x_flat = [model.intvar(0, size - 1, name=f"x_{s}") for s in range(size)]
    # where[k] = the square the knight stands on at move number k. It is the inverse of
    # x_flat and lets "the knight moves from move k to move k + 1" be a rule on pairs of squares.
    where = [model.intvar(0, size - 1, name=f"where_{k}") for k in range(size)]

    # each square is visited exactly once (the move numbers are a permutation of 0..n*n-1)
    model.all_different(x_flat).post()
    model.inverse_channeling(x_flat, where).post()

    # pairs of squares that are a knight's move apart
    knight_moves_apart = []
    for i in range(n):
        for j in range(n):
            for di, dj in KNIGHT_MOVES:
                if 0 <= i + di < n and 0 <= j + dj < n:
                    knight_moves_apart.append([i * n + j, (i + di) * n + (j + dj)])

    # the square of move k + 1 is a knight's move away from the square of move k
    for k in range(size - 1):
        model.table([where[k], where[k + 1]], knight_moves_apart).post()

    x = [[x_flat[i * n + j] for j in range(n)] for i in range(n)]
    return model, {"x": x}
