# Maximum density still life on an n x m active grid (CSPLib 032).
#
# A still life is a pattern that does not change from one generation to the next
# (Conway's Game of Life). Cells outside the active grid are dead and are not
# printed, but they can still be born, so the birth rule is also checked on the
# ring of dead cells around the grid. The objective is the number of live cells.
#
# Encoding: one Bool per cell. The number of live neighbours of a cell is a linear
# sum of its (up to 8) neighbour Bools, so every rule is a PB constraint on that
# sum. Cells outside the grid are constant dead, so their neighbour sums simply
# leave out the out-of-grid positions.

from paramita.modelling import Bool, If, Or


def build(instance):
    n, m = instance["n"], instance["m"]

    # c[i][j] = 1 if the cell in row i, column j of the active grid is alive
    c = [[Bool(f"c_{i}_{j}") for j in range(m)] for i in range(n)]

    def inside(i, j):
        return 0 <= i < n and 0 <= j < m

    def neighbours(i, j):
        # the number of live neighbours of (i, j), counting in-grid cells only
        return sum(
            c[i + di][j + dj]
            for di in (-1, 0, 1)
            for dj in (-1, 0, 1)
            if (di, dj) != (0, 0) and inside(i + di, j + dj)
        )

    cons = []

    # a live cell must have exactly 2 or 3 live neighbours to stay alive
    for i in range(n):
        for j in range(m):
            nb = neighbours(i, j)
            cons.append(If(c[i][j], (nb >= 2) & (nb <= 3)))

    # a dead cell must not have exactly 3 live neighbours (otherwise it is born).
    # This covers the cells of the grid and the ring of dead cells around it.
    for i in range(-1, n + 1):
        for j in range(-1, m + 1):
            nb = neighbours(i, j)
            if inside(i, j):
                cons.append(Or([c[i][j], nb <= 2, nb >= 4]))
            else:
                cons.append(Or([nb <= 2, nb >= 4]))

    # maximise the number of live cells
    density = sum(c[i][j] for i in range(n) for j in range(m))

    grid = [[c[i][j] for j in range(m)] for i in range(n)]
    return cons, {"grid": grid}, ("maximize", density)
