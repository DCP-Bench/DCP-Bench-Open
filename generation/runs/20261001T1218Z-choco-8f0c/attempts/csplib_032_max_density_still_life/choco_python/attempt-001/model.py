# Maximum density still life (CSPLib 32): on an n x m window of Conway's Game of Life, with every
# cell outside the window dead, find the stable pattern with the most live cells in the window.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # rows of the active grid
    m = instance["m"]  # columns of the active grid

    model = Model()

    # grid[i][j] is true when the cell in row i, column j is alive
    grid = [[model.boolvar(name=f"grid_{i}_{j}") for j in range(m)] for i in range(n)]

    # Still-life rule as (live neighbours, cell) pairs: a dead cell may have any number of live
    # neighbours except exactly 3 (it would be born); a live cell needs exactly 2 or 3 (it survives).
    rule = [(k, 0) for k in range(9) if k != 3] + [(2, 1), (3, 1)]

    # In-grid still-life rules: count each cell's live neighbours inside the window and require the
    # (count, cell) pair to follow the rule.
    for i in range(n):
        for j in range(m):
            neighbours = [grid[i + di][j + dj]
                          for di in (-1, 0, 1) for dj in (-1, 0, 1)
                          if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < m]
            alive = model.intvar(0, len(neighbours), name=f"alive_{i}_{j}")
            model.sum(neighbours, "=", alive).post()
            model.table([alive, grid[i][j]], [t for t in rule if t[0] <= len(neighbours)]).post()

    # Ghost-boundary rules: a dead cell just outside the window must not be born, so it must not
    # see exactly 3 live cells. Outside the top and bottom rows it sees three consecutive cells of
    # that row; outside the left and right columns, three consecutive cells of that column.
    for j in range(m):
        cols = range(max(0, j - 1), min(m, j + 2))
        model.sum([grid[0][c] for c in cols], "!=", 3).post()
        model.sum([grid[n - 1][c] for c in cols], "!=", 3).post()
    for i in range(n):
        rows = range(max(0, i - 1), min(n, i + 2))
        model.sum([grid[r][0] for r in rows], "!=", 3).post()
        model.sum([grid[r][m - 1] for r in rows], "!=", 3).post()

    # Maximise the number of live cells in the window.
    live = model.intvar(0, n * m, name="live")
    model.sum([cell for row in grid for cell in row], "=", live).post()

    return model, {"grid": grid}, ("maximize", live)
