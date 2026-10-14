"""N-puzzle: slide the tiles of a square sliding puzzle from a start state to an end state in exactly N_STEPS states."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_steps = instance["N_STEPS"]
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    dim = len(start)
    n = dim * dim - 1          # tiles 1..n plus the empty tile 0
    cells = [(i, j) for i in range(dim) for j in range(dim)]
    steps = range(n_steps)

    def neighbours(i, j):
        # The cells the empty tile can slide to from (i, j): left, right, up, down.
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= i + di < dim and 0 <= j + dj < dim:
                yield i + di, j + dj

    model = gp.Model("n_puzzle")

    # x[t, i, j]: the tile on cell (i, j) at step t. The first step is the start
    # state and the last step the end state, fixed through the variable bounds.
    x = {}
    blank = {}
    for t in steps:
        for (i, j) in cells:
            fixed = start[i][j] if t == 0 else end[i][j] if t == n_steps - 1 else None
            lo, hi = (fixed, fixed) if fixed is not None else (0, n)
            x[t, i, j] = model.addVar(lb=lo, ub=hi, vtype=GRB.INTEGER, name=f"x[{t},{i},{j}]")
            # blank[t, i, j] is 1 when the empty tile is on cell (i, j) at step t.
            if fixed is not None:
                b = 1 if fixed == 0 else 0
                blank[t, i, j] = model.addVar(lb=b, ub=b, vtype=GRB.BINARY, name=f"blank[{t},{i},{j}]")
            else:
                blank[t, i, j] = model.addVar(vtype=GRB.BINARY, name=f"blank[{t},{i},{j}]")

    total = sum(start[i][j] for (i, j) in cells)
    for t in steps:
        # Each state has exactly one empty tile, since all its cells hold different values 0..n.
        model.addConstr(gp.quicksum(blank[t, i, j] for (i, j) in cells) == 1, name=f"one_blank[{t}]")
        if 0 < t < n_steps - 1:
            for (i, j) in cells:
                # A cell holds 0 exactly when the empty tile is on it.
                model.addConstr(x[t, i, j] <= n * (1 - blank[t, i, j]), name=f"zero[{t},{i},{j}]")
                model.addConstr(x[t, i, j] >= 1 - blank[t, i, j], name=f"tile[{t},{i},{j}]")
            # Every state holds the same tiles as the start state. Together with the two
            # constraints below this keeps the cells all different: the only cells that
            # change are the old and the new place of the empty tile, the new place
            # becomes 0, so the old place must take the tile that slid out of the new one.
            model.addConstr(gp.quicksum(x[t, i, j] for (i, j) in cells) == total, name=f"same_tiles[{t}]")

    for t in range(1, n_steps):
        for (i, j) in cells:
            # The empty tile reaches (i, j) only from a neighbouring cell. Staying in place
            # is excluded: then no cell could change, and the state must change every step.
            model.addConstr(blank[t, i, j] <= gp.quicksum(blank[t - 1, r, c] for (r, c) in neighbours(i, j)),
                            name=f"slide[{t},{i},{j}]")
            # Only the cells where the empty tile was or is now may change; n bounds the change.
            moved = blank[t - 1, i, j] + blank[t, i, j]
            model.addConstr(x[t, i, j] - x[t - 1, i, j] <= n * moved, name=f"keep_up[{t},{i},{j}]")
            model.addConstr(x[t - 1, i, j] - x[t, i, j] <= n * moved, name=f"keep_down[{t},{i},{j}]")

    return model, {"steps": [[[x[t, i, j] for j in range(dim)] for i in range(dim)] for t in steps]}
