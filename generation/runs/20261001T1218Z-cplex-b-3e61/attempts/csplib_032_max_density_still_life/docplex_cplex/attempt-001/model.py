"""Maximum density still life: on an n-by-m patch of Conway's Game of Life board (every cell
outside it dead), find a pattern that does not change from one generation to the next with as
many live cells as possible.

The model reports the pattern, 1 for a live cell.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # rows of the active grid
    m = instance["m"]  # columns of the active grid

    model = Model("still_life")

    grid = [[model.binary_var(name=f"grid_{i}_{j}") for j in range(m)] for i in range(n)]

    for i in range(n):
        for j in range(m):
            around = [grid[i + a][j + b] for a in (-1, 0, 1) for b in (-1, 0, 1)
                      if (a, b) != (0, 0) and 0 <= i + a < n and 0 <= j + b < m]
            k = model.sum(around)  # live neighbours of cell (i, j)
            deg = len(around)
            alive = grid[i][j]

            # A live cell has exactly 2 or 3 live neighbours (the bounds switch off when dead).
            model.add_constraint(k >= 2 * alive)
            if deg > 3:
                model.add_constraint(k <= 3 + (deg - 3) * (1 - alive))

            # A dead cell does not have exactly 3 live neighbours: it has at most 2 (many = 0)
            # or at least 4 (many = 1). Both bounds are relaxed for a live cell.
            many = model.binary_var(name=f"many_{i}_{j}")
            model.add_constraint(k <= 2 + max(0, deg - 2) * many + alive)
            model.add_constraint(k >= 4 * many - 4 * alive)

    # Cells just outside the grid are dead and must not be born: an outside cell next to three
    # cells of the grid's border must not see all three alive. Outside cells that touch fewer
    # border cells can never see three.
    windows = []
    for j in range(1, m - 1):
        windows.append([grid[0][j - 1], grid[0][j], grid[0][j + 1]])
        windows.append([grid[n - 1][j - 1], grid[n - 1][j], grid[n - 1][j + 1]])
    for i in range(1, n - 1):
        windows.append([grid[i - 1][0], grid[i][0], grid[i + 1][0]])
        windows.append([grid[i - 1][m - 1], grid[i][m - 1], grid[i + 1][m - 1]])
    for w in windows:
        model.add_constraint(model.sum(w) <= 2)

    # Maximize the number of live cells.
    model.maximize(model.sum(grid[i][j] for i in range(n) for j in range(m)))

    return model, {"grid": grid}
