# CSPLib 032, maximum density still life, on an n x m active grid.
# grid[i][j] = 1 when cell (i, j) of the active grid is alive. Cells outside the grid are dead.
# The rules below apply to the dead ring just outside the grid as well as to the grid itself.
import mip


def build(instance):
    n = instance["n"]
    m = instance["m"]
    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    grid = [[model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(m)] for i in range(n)]

    def live(i, j):
        # the variable of a live cell inside the active grid, None for a dead cell outside it
        if 0 <= i < n and 0 <= j < m:
            return grid[i][j]
        return None

    def live_neighbours(i, j):
        # the variables of the live neighbours of (i, j) that lie inside the active grid
        terms = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                v = live(i + di, j + dj)
                if v is not None:
                    terms.append(v)
        return terms

    # A live cell must have exactly 2 or 3 live neighbors to remain alive.
    # A live cell has at most 8 neighbours, so the big-M constant 5 = 8 - 3 is exact.
    for i in range(n):
        for j in range(m):
            x = grid[i][j]
            s = mip.xsum(live_neighbours(i, j))
            model.add_constr(s >= 2 * x)
            model.add_constr(s <= 3 + 5 * (1 - x))

    # A dead cell, including any dead cell just outside the active grid, must not have exactly 3 live neighbors.
    # Binary b = 1 forces at least 4 live neighbours, b = 0 forces at most 2, so 3 is excluded.
    # A live cell (x = 1) relaxes both rows. The constants come from the neighbour count range 0..8.
    for i in range(-1, n + 1):
        for j in range(-1, m + 1):
            x = live(i, j)
            b = model.add_var(f"b_{i + 1}_{j + 1}", var_type=mip.BINARY)
            s = mip.xsum(live_neighbours(i, j))
            if x is None:
                model.add_constr(s <= 2 + 6 * b)
                model.add_constr(s >= 4 * b)
            else:
                model.add_constr(s <= 2 + 6 * b + 8 * x)
                model.add_constr(s >= 4 * b - 4 * x)

    # Maximise the number of live cells in the active grid.
    model.objective = mip.xsum(grid[i][j] for i in range(n) for j in range(m))

    return model, {"grid": grid}
