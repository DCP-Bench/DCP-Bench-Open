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
    neighbours = {}
    for i in range(n):
        for j in range(n):
            neighbours[(i, j)] = [
                (i + di, j + dj)
                for di, dj in moves
                if 0 <= i + di < n and 0 <= j + dj < n
            ]

    for i in range(n):
        for j in range(n):
            successors = [x[a][b] == x[i][j] + 1 for a, b in neighbours[(i, j)]]
            constraints.append(cz.Or([x[i][j] == cells - 1] + successors))

    # Redundant: every move number except the first is reached from a square
    # one knight's move away carrying the previous move number. This is implied
    # by the successor rule and by Distinct, and it gives the solver direct
    # propagation in both directions.
    for i in range(n):
        for j in range(n):
            predecessors = [x[a][b] == x[i][j] - 1 for a, b in neighbours[(i, j)]]
            constraints.append(cz.Or([x[i][j] == 0] + predecessors))

    return constraints, {"x": x}
