# Maximum density still life (CSPLib 032): fill an n x m grid of Game of
# Life cells, everything outside it dead, so that the pattern never changes,
# with as many live cells as possible.
from itertools import product

from pysat.formula import IDPool, WCNF


def build(instance):
    n = instance["n"]
    m = instance["m"]

    pool = IDPool()
    formula = WCNF()

    # grid[i][j] is true when the cell in row i, column j is alive.
    grid = [[pool.id(("grid", i, j)) for j in range(m)] for i in range(n)]

    # Inside the grid: a live cell has exactly 2 or 3 live neighbours, and a
    # dead cell does not have exactly 3 (or it would be born). A cell and its
    # at most 8 neighbours take at most 512 joint values, so every
    # combination that breaks the rule is forbidden by its own clause; unit
    # propagation then enforces the rule completely.
    for i in range(n):
        for j in range(m):
            neighbours = [grid[a][b]
                          for a in range(i - 1, i + 2) for b in range(j - 1, j + 2)
                          if (a, b) != (i, j) and 0 <= a < n and 0 <= b < m]
            for alive in (True, False):
                for values in product((True, False), repeat=len(neighbours)):
                    count = sum(values)
                    ok = count in (2, 3) if alive else count != 3
                    if not ok:
                        clause = [-grid[i][j] if alive else grid[i][j]]
                        clause += [-lit if v else lit for lit, v in zip(neighbours, values)]
                        formula.append(clause)

    # Just outside the grid: a dead cell beside the border sees the (up to 3)
    # border cells next to it, and must not see exactly 3 live ones.
    border = []
    for j in range(m):
        cols = range(max(0, j - 1), min(m, j + 2))
        border.append([grid[0][b] for b in cols])
        border.append([grid[n - 1][b] for b in cols])
    for i in range(n):
        rows = range(max(0, i - 1), min(n, i + 2))
        border.append([grid[a][0] for a in rows])
        border.append([grid[a][m - 1] for a in rows])
    for cells in border:
        if len(cells) == 3:
            formula.append([-lit for lit in cells])

    # Maximise the number of live cells: every dead cell pays 1.
    for row in grid:
        for lit in row:
            formula.append([lit], weight=1)

    return formula, {"grid": grid}
