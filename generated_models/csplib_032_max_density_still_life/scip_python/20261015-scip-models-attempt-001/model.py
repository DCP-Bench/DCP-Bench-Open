# Maximum-density still life: choose live cells on an n x m grid so the pattern is stable and has as many live cells as possible.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = instance["m"]
    model = Model()

    # x[r, c] = 1 if the cell in the active n x m grid is alive
    x = {(r, c): model.addVar(name=f"x_{r}_{c}", vtype="B") for r in range(n) for c in range(m)}

    def neighbours(r, c):
        # the in-grid cells around (r, c); cells outside the grid are dead, so they are left out
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r + dr < n and 0 <= c + dc < m]

    def not_exactly_three(r, c, alive=None):
        # a dead cell must not have exactly 3 live neighbours:
        # lo = 1 forces at most 2 live neighbours, hi = 1 forces at least 4
        count = quicksum(x[p] for p in neighbours(r, c))
        lo = model.addVar(name=f"lo_{r}_{c}", vtype="B")
        hi = model.addVar(name=f"hi_{r}_{c}", vtype="B")
        model.addConsIndicator(count <= 2, binvar=lo)
        model.addConsIndicator(count >= 4, binvar=hi)
        if alive is None:
            # outside the grid the cell is always dead
            model.addCons(lo + hi >= 1)
        else:
            # inside the grid the rule only applies when the cell is dead
            model.addCons(lo + hi + alive >= 1)

    # live cells in the grid have 2 or 3 live neighbours
    # ("a live cell must have exactly 2 or 3 live neighbors to remain alive")
    for r in range(n):
        for c in range(m):
            count = quicksum(x[p] for p in neighbours(r, c))
            model.addConsIndicator(count >= 2, binvar=x[r, c])
            model.addConsIndicator(count <= 3, binvar=x[r, c])

    # dead cells in the grid do not have exactly 3 live neighbours
    # ("a dead cell must not have exactly 3 live neighbors")
    for r in range(n):
        for c in range(m):
            not_exactly_three(r, c, alive=x[r, c])

    # dead cells just outside the grid must not have exactly 3 live neighbours
    # (they can still be born from the pattern on the grid border)
    for r in range(-1, n + 1):
        for c in range(-1, m + 1):
            if 0 <= r < n and 0 <= c < m:
                continue
            # a cell with fewer than 3 in-grid neighbours cannot have 3 live ones
            if len(neighbours(r, c)) < 3:
                continue
            not_exactly_three(r, c)

    # maximise the number of live cells in the active grid
    model.setObjective(quicksum(x[r, c] for r in range(n) for c in range(m)), "maximize")

    grid = [[x[r, c] for c in range(m)] for r in range(n)]
    return model, {"grid": grid}
