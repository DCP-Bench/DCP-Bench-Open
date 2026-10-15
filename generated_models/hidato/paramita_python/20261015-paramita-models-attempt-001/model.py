# Hidato puzzle on an n*n grid: fill every empty cell with a number so that
# the numbers 1..n^2 each appear once, the given tiles stay in place, and each
# number touches the next one horizontally, vertically or diagonally.
from paramita.modelling import Bool, Or


def build(instance):
    puzzle = instance["puzzle"]
    n = len(puzzle)
    N = n * n
    values = range(1, N + 1)
    cells = [(i, j) for i in range(n) for j in range(n)]

    # One-hot encoding: x[(i, j)][v] is true when cell (i, j) holds the number v.
    x = {(i, j): {v: Bool(f"x_{i}_{j}_{v}") for v in values} for i, j in cells}

    cons = []

    # every cell holds exactly one number
    for c in cells:
        cons.append(sum(x[c][v] for v in values) == 1)
    # every number from 1 to n^2 is placed in exactly one cell
    for v in values:
        cons.append(sum(x[c][v] for c in cells) == 1)

    # the numbered tiles of the puzzle stay where they are
    for i, j in cells:
        if puzzle[i][j] != 0:
            cons.append(x[(i, j)][puzzle[i][j]])

    # each number touches the next one horizontally, vertically or diagonally:
    # if k is in cell c, then k + 1 is in one of the neighbours of c
    for i, j in cells:
        nbrs = [
            (i + di, j + dj)
            for di in (-1, 0, 1)
            for dj in (-1, 0, 1)
            if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < n
        ]
        for k in range(1, N):
            cons.append(~x[(i, j)][k] | Or([x[d][k + 1] for d in nbrs]))

    outputs = {
        "x": [[sum(v * x[(i, j)][v] for v in values) for j in range(n)] for i in range(n)]
    }
    return cons, outputs
