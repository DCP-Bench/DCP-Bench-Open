# Hidato: fill an R x C grid with the numbers 1 to R*C, each used once, keeping the given
# numbers, so that each number touches the next one horizontally, vertically or diagonally.
from pyscipopt import Model, quicksum


def build(instance):
    puzzle = instance["puzzle"]
    R = len(puzzle)
    C = len(puzzle[0])
    N = R * C
    values = range(1, N + 1)
    cells = [(i, j) for i in range(R) for j in range(C)]
    m = Model("hidato")

    # b[i, j, v] = 1 if the cell in row i, column j holds the number v
    b = {(i, j, v): m.addVar(name=f"b_{i}_{j}_{v}", vtype="B") for (i, j) in cells for v in values}

    # each cell holds exactly one number
    for (i, j) in cells:
        m.addCons(quicksum(b[i, j, v] for v in values) == 1)

    # each number from 1 to R*C is placed exactly once
    for v in values:
        m.addCons(quicksum(b[i, j, v] for (i, j) in cells) == 1)

    # the given numbers of the puzzle stay where they are
    for (i, j) in cells:
        if puzzle[i][j] > 0:
            m.addCons(b[i, j, puzzle[i][j]] == 1)

    # consecutive numbers touch: if v is in a cell, v+1 is in one of its 8 neighbours
    def neighbours(i, j):
        return [(i + di, j + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1)
                if (di, dj) != (0, 0) and 0 <= i + di < R and 0 <= j + dj < C]

    for v in range(1, N):
        for (i, j) in cells:
            m.addCons(quicksum(b[q, r, v + 1] for (q, r) in neighbours(i, j)) >= b[i, j, v])

    # the grid as a list of lists of the number in each cell
    grid = [[quicksum(v * b[i, j, v] for v in values) for j in range(C)] for i in range(R)]
    return m, {"x": grid}
