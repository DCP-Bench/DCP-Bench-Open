"""Maximum density still life: the most live cells in an n x m Game of Life pattern that does not change, with all cells outside the grid dead."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    m = instance["m"]

    model = gp.Model("still_life")

    # grid[i, j] is 1 when cell (i, j) is alive.
    grid = model.addVars(n, m, vtype=GRB.BINARY, name="grid")

    for i in range(n):
        for j in range(m):
            neighbours = [grid[i + di, j + dj] for di in (-1, 0, 1) for dj in (-1, 0, 1)
                          if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < m]
            k = len(neighbours)      # number of neighbours inside the grid
            live = gp.quicksum(neighbours)

            # A live cell has exactly 2 or 3 live neighbours; k bounds the count otherwise.
            model.addConstr(live >= 2 * grid[i, j], name=f"live_lo[{i},{j}]")
            if k > 3:
                model.addConstr(live <= 3 + (k - 3) * (1 - grid[i, j]), name=f"live_hi[{i},{j}]")

            # A dead cell must not have exactly 3 live neighbours: it has at most 2
            # (fewer) or at least 4 (more).
            if k >= 3:
                fewer = model.addVar(vtype=GRB.BINARY, name=f"fewer[{i},{j}]")
                more = model.addVar(vtype=GRB.BINARY, name=f"more[{i},{j}]")
                model.addConstr(fewer + more >= 1 - grid[i, j], name=f"not_born[{i},{j}]")
                model.addConstr((fewer == 1) >> (live <= 2))
                model.addConstr((more == 1) >> (live >= 4))

    # Dead cells just outside the grid must not be born: their live neighbours are the
    # (up to three) adjacent cells of the border row or column, which must not all be alive.
    for j in range(m):
        cols = range(max(0, j - 1), min(m, j + 2))
        if len(cols) == 3:
            model.addConstr(gp.quicksum(grid[0, c] for c in cols) <= 2, name=f"top[{j}]")
            model.addConstr(gp.quicksum(grid[n - 1, c] for c in cols) <= 2, name=f"bottom[{j}]")
    for i in range(n):
        rows = range(max(0, i - 1), min(n, i + 2))
        if len(rows) == 3:
            model.addConstr(gp.quicksum(grid[r, 0] for r in rows) <= 2, name=f"left[{i}]")
            model.addConstr(gp.quicksum(grid[r, m - 1] for r in rows) <= 2, name=f"right[{i}]")

    # Maximise the number of live cells in the grid.
    model.setObjective(grid.sum(), GRB.MAXIMIZE)

    return model, {"grid": [[grid[i, j] for j in range(m)] for i in range(n)]}
