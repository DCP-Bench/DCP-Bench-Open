# Knight's tour on an n x n chessboard (n read from the instance).
# The tour visits every square exactly once; x[i][j] is the move number of
# the knight on square (i, j), numbered 0 to n*n-1. The tour does not need to
# return to its starting square, and the description does not fix the start.

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    cells = n * n
    x = [[cz.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    constraints = []

    # The description: the tour is represented by integers from 0 to n*n-1,
    # each square visited exactly once.
    for i in range(n):
        for j in range(n):
            constraints.append(x[i][j] >= 0)
            constraints.append(x[i][j] <= cells - 1)
    constraints.append(cz.Distinct([x[i][j] for i in range(n) for j in range(n)]))

    # The description: the knight moves from one move number to the next.
    # Every square except the last move is followed by a square one knight's
    # move away that carries the next move number.
    moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    for i in range(n):
        for j in range(n):
            successors = []
            for di, dj in moves:
                a, b = i + di, j + dj
                if 0 <= a < n and 0 <= b < n:
                    successors.append(x[a][b] == x[i][j] + 1)
            constraints.append(cz.Or([x[i][j] == cells - 1] + successors))

    return constraints, {"x": x}
