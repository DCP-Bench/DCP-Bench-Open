"""Knight's tour: number the squares of an n-by-n chessboard 0..n*n-1 in the order a knight visits
them, so that every square is visited exactly once and each move is a knight's move. The tour is
open: it does not have to return to its starting square.

The model reports the move number of every square.
"""
from docplex.mp.model import Model

# The eight jumps a knight can make (a property of the piece, not of the instance).
KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def build(instance):
    n = instance["n"]  # size of the chessboard
    squares = [(i, j) for i in range(n) for j in range(n)]
    last = n * n - 1

    model = Model("knights_tour")

    # x[i][j] is the move number at which the knight stands on square (i, j).
    x = {sq: model.integer_var(0, last, name=f"x_{sq[0]}_{sq[1]}") for sq in squares}

    # The tour is encoded by its moves rather than by a one-hot square-to-number table:
    # jump[a, b] = 1 when the knight goes from square a straight to square b. There is one
    # binary per knight move on the board (576 at n = 10), where the one-hot table would need
    # n**4 binaries and exceed the Community Edition's 1000-variable limit.
    jump = {}
    for (i, j) in squares:
        for di, dj in KNIGHT_MOVES:
            if 0 <= i + di < n and 0 <= j + dj < n:
                jump[(i, j), (i + di, j + dj)] = model.binary_var(name=f"jump_{i}_{j}_{i + di}_{j + dj}")

    # The knight leaves every square at most once and arrives on every square at most once.
    for sq in squares:
        model.add_constraint(model.sum(v for (a, b), v in jump.items() if a == sq) <= 1)
        model.add_constraint(model.sum(v for (a, b), v in jump.items() if b == sq) <= 1)

    # Visiting n*n squares takes n*n - 1 moves.
    model.add_constraint(model.sum(jump.values()) == last)

    # A move from a to b means b is visited right after a. The move numbers then rise by one
    # along every chain of moves, so no chain can close into a loop; with n*n - 1 moves and at
    # most one move in and out of each square, the moves form a single path through all
    # squares, numbered 0..n*n-1 in visiting order (hence every square gets a different number).
    for (a, b), v in jump.items():
        model.add_indicator(v, x[b] == x[a] + 1)

    return model, {"x": [[x[i, j] for j in range(n)] for i in range(n)]}
