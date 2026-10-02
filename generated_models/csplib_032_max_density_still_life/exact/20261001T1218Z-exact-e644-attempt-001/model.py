# Maximum density still life (CSPLib 32): on an n x m grid of the Game of Life, with all cells
# outside the grid dead, find the stable pattern with the most live cells.
from exact import Exact


def build(instance):
    n = instance["n"]  # rows of the active grid
    m = instance["m"]  # columns of the active grid

    solver = Exact()

    # grid[i][j] = 1 if cell (i, j) is alive
    grid = [[f"grid_{i}_{j}" for j in range(m)] for i in range(n)]
    for i in range(n):
        for j in range(m):
            solver.addVariable(grid[i][j], 0, 1)

    # In-grid still-life rules. s = number of live neighbours of the cell, a sum of grid cells.
    for i in range(n):
        for j in range(m):
            neighbors = [grid[i + dx][j + dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                         if (dx or dy) and 0 <= i + dx < n and 0 <= j + dy < m]
            k = len(neighbors)
            s = [(1, name) for name in neighbors]
            cell = grid[i][j]
            # a live cell needs at least 2 live neighbours: s >= 2 * cell
            solver.addConstraint(s + [(-2, cell)], True, 0)
            # a live cell needs at most 3 live neighbours: s <= 3 when alive (s <= k always)
            if k > 3:
                solver.addConstraint(s + [(k - 3, cell)], False, 0, True, k)
            # a dead cell must not have exactly 3 live neighbours. Exact has no "not equal", so
            # the switch avoid3[i][j] says on which side of 3 the neighbour count lies:
            # 0 = at most 2 (at most 3 for a live cell), 1 = at least 4.
            if k >= 3:
                avoid3 = f"avoid3_{i}_{j}"
                solver.addVariable(avoid3, 0, 1)
                solver.addConstraint(s + [(-1, cell), (-(k - 2), avoid3)], False, 0, True, 2)
                solver.addConstraint(s + [(-4, avoid3), (2, cell)], True, 0)

    # Ghost-boundary rules: cells outside the grid are dead and must not be born, so no outside
    # cell may have exactly 3 live neighbours. An outside cell next to the top or bottom row sees
    # three consecutive cells of that row; one next to the left or right column sees three
    # consecutive cells of that column. (Fewer than three cells cannot sum to 3.)
    for j in range(m):
        for row in (0, n - 1):
            window = [grid[row][jj] for jj in range(max(0, j - 1), min(m, j + 2))]
            if len(window) == 3:
                solver.addConstraint([(1, name) for name in window], False, 0, True, 2)
    for i in range(n):
        for col in (0, m - 1):
            window = [grid[ii][col] for ii in range(max(0, i - 1), min(n, i + 2))]
            if len(window) == 3:
                solver.addConstraint([(1, name) for name in window], False, 0, True, 2)

    # maximise the number of live cells in the active grid
    return (solver, {"grid": grid},
            ("maximize", [(1, grid[i][j]) for i in range(n) for j in range(m)]))
