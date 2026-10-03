# Knight's tour: number the squares of an n x n board 0..n*n-1 so that a knight
# can walk through them in numerical order, moving from each square to the
# next with a knight's move. The tour does not have to return to its start.
import functools
import operator

from hermax.model import Model

# The eight moves of a knight. These belong to the rules of chess, not the instance.
KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def build(instance):
    n = instance["n"]  # board size
    squares = n * n  # numbers run from 0 to squares - 1

    m = Model()
    # x[i][j] = the move number at which the knight is on square (i, j) (the declared output)
    x = m.int_matrix("x", n, n, 0, squares - 1)
    # holds[s][k] = square s = i * n + j has move number k (one-hot form of x)
    holds = m.bool_matrix("holds", squares, squares)

    # every square is visited at exactly one move number, and every move number is used once
    for s in range(squares):
        m &= holds.row(s).exactly_one()
        m &= holds.col(s).exactly_one()
    for i in range(n):
        for j in range(n):
            for k in range(squares):
                m &= (~holds[i * n + j][k] | (x[i][j] == k))

    # The squares a knight can reach from (i, j) in one move.
    def moves(i, j):
        return [(i + di) * n + (j + dj) for di, dj in KNIGHT_MOVES
                if 0 <= i + di < n and 0 <= j + dj < n]

    # The knight moves from one numbered square to the next: if a square has
    # number k, a knight's move away there is a square with number k + 1, and
    # (for k > 0) one with number k - 1. Each number is used once, so that
    # square is unique.
    for i in range(n):
        for j in range(n):
            reach = moves(i, j)
            for k in range(squares):
                if k < squares - 1:
                    m &= (~holds[i * n + j][k] | functools.reduce(operator.or_, [holds[s][k + 1] for s in reach]))
                if k > 0:
                    m &= (~holds[i * n + j][k] | functools.reduce(operator.or_, [holds[s][k - 1] for s in reach]))

    return m, {"x": x}
