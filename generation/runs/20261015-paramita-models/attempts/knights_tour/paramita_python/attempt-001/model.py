# Knight's tour: a knight moves on an n x n board and visits every square exactly once.
# The tour is written as move numbers 0..n*n-1: x[i][j] is the move at which the knight
# is on square (i, j). Each move k has one-hot step Bools v[k][s] (the knight is on square s
# at move k); the move number of a square is the integer sum over k of k * v[k][s].
# The tour is open: it does not have to return to the starting square.

from paramita.modelling import Bool, If, Or


def build(instance):
    n = instance["n"]
    squares = [(i, j) for i in range(n) for j in range(n)]
    moves = n * n
    index = {s: idx for idx, s in enumerate(squares)}

    # v[k][s] = 1 if the knight is on square s at move k
    v = [[Bool(f"v_{k}_{s}") for s in range(moves)] for k in range(moves)]

    # knight moves: the two steps of a knight, in each of the 8 directions
    deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    neighbours = {}
    for s, (i, j) in enumerate(squares):
        neighbours[s] = [
            index[(i + di, j + dj)]
            for di, dj in deltas
            if 0 <= i + di < n and 0 <= j + dj < n
        ]

    cons = []
    # every move is made on exactly one square
    cons += [sum(v[k]) == 1 for k in range(moves)]
    # the knight visits every square exactly once
    cons += [sum(v[k][s] for k in range(moves)) == 1 for s in range(moves)]
    # each move is a knight move: from the square at move k, the knight is on a
    # square a knight can reach at move k + 1
    for k in range(moves - 1):
        for s in range(moves):
            cons.append(If(v[k][s], Or([v[k + 1][t] for t in neighbours[s]])))

    # the move number of each square is the value of its one-hot step
    x = [
        [sum(k * v[k][index[(i, j)]] for k in range(moves)) for j in range(n)]
        for i in range(n)
    ]

    return cons, {"x": x}
