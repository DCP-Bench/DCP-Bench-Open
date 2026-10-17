# Knight's tour on an n x n chessboard (n read from the instance).
# The tour visits every square exactly once; x[i][j] is the move number of
# the knight on square (i, j), numbered 0 to n*n-1. The tour does not need to
# return to its starting square, and the description does not fix the start.

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    cells = n * n

    # Sequence view: step k is the square row[k], col[k] visited on move k.
    row = [cz.Int(f"row_{k}") for k in range(cells)]
    col = [cz.Int(f"col_{k}") for k in range(cells)]

    constraints = []

    # The description: the board is n x n, every square is on the board.
    for k in range(cells):
        constraints.append(row[k] >= 0)
        constraints.append(row[k] <= n - 1)
        constraints.append(col[k] >= 0)
        constraints.append(col[k] <= n - 1)

    # The description: each square is visited exactly once, so the move
    # squares are all different. Distinct over the square numbers does this.
    constraints.append(
        cz.Distinct([row[k] * n + col[k] for k in range(cells)])
    )

    # The description: a knight moves in an L shape from one move to the next.
    moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    for k in range(cells - 1):
        constraints.append(
            cz.Or(
                [
                    cz.And(row[k + 1] == row[k] + di, col[k + 1] == col[k] + dj)
                    for di, dj in moves
                ]
            )
        )

    # Output: the move number of each square is the step k at which the
    # sequence visits that square.
    x = []
    for i in range(n):
        line = []
        for j in range(n):
            v = cz.Int(f"x_{i}_{j}")
            constraints.append(v >= 0)
            constraints.append(v <= cells - 1)
            constraints.append(
                cz.Or(
                    [
                        cz.And(row[k] == i, col[k] == j, v == k)
                        for k in range(cells)
                    ]
                )
            )
            line.append(v)
        x.append(line)

    return constraints, {"x": x}
