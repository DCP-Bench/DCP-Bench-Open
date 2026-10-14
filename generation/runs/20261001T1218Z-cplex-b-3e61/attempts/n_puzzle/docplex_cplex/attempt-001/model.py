"""N-puzzle: on a square board of numbered tiles with one empty cell (0), find the sequence of
N_STEPS board states from the start state to the end state in which every step slides one tile
into the empty cell; the board has to change at every step.

The model reports the board at every step, start and end included.
"""
from docplex.mp.model import Model


def build(instance):
    T = instance["N_STEPS"]          # number of board states, start and end included
    start = instance["puzzle_start"]  # board at the first step; 0 is the empty cell
    end = instance["puzzle_end"]      # board at the last step
    dim = len(start)
    cells = [(i, j) for i in range(dim) for j in range(dim)]
    tiles = range(dim * dim)          # 0 (empty) and the tiles 1..dim*dim-1
    M = dim * dim - 1                 # largest tile number: the widest change of a cell

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbours(c):
        return [(c[0] + a, c[1] + b) for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if 0 <= c[0] + a < dim and 0 <= c[1] + b < dim]

    at_start = {start[i][j]: (i, j) for i, j in cells}
    at_end = {end[i][j]: (i, j) for i, j in cells}

    # Which tile can stand on which cell at which step. Every step slides exactly one tile one
    # cell, so the T - 1 steps are shared by all tiles: tile v travels at least the distance
    # between its start and end cells, and at most that plus the slack the other tiles leave.
    # The empty cell moves at every step, so its distance from its start has the parity of the
    # step. These are consequences of the rules, not extra rules; they keep the one-hot
    # encoding below inside the Community Edition's 1000-variable limit (496 binaries on the
    # 4x4 instance instead of 13 * 16 * 16).
    least = sum(dist(at_start[v], at_end[v]) for v in tiles if v != 0)
    slack = (T - 1) - least

    def possible(t, c, v):
        if v not in at_start or v not in at_end:
            return False
        a, b = dist(at_start[v], c), dist(c, at_end[v])
        if a > t or b > T - 1 - t:
            return False
        if v == 0:
            return (t - a) % 2 == 0
        return a + b <= dist(at_start[v], at_end[v]) + slack

    model = Model("n_puzzle")

    # holds[t, c, v] = 1 when cell c shows tile v at step t. The first and last boards are given.
    holds = {}
    for t in range(T):
        for c in cells:
            for v in tiles:
                if t == 0:
                    holds[t, c, v] = 1 if start[c[0]][c[1]] == v else 0
                elif t == T - 1:
                    holds[t, c, v] = 1 if end[c[0]][c[1]] == v else 0
                elif possible(t, c, v):
                    holds[t, c, v] = model.binary_var(name=f"holds_{t}_{c[0]}_{c[1]}_{v}")

    def expr(items):
        e = model.linear_expr()
        for item in items:
            e += item
        return e

    def blank(t, c):
        return expr([holds.get((t, c, 0), 0)])

    # x[t][c] is the tile on cell c at step t.
    x = {(t, c): expr([v * holds[t, c, v] for v in tiles if (t, c, v) in holds])
         for t in range(T) for c in cells}

    impossible = []

    def post(left, sense, right):
        # A relation between constants is checked here: docplex needs a variable to post one.
        d = left - right
        if d.is_constant():
            k = d.constant
            if not ((sense == "<=" and k <= 0) or (sense == "==" and k == 0) or (sense == ">=" and k >= 0)):
                impossible.append(True)
            return
        if sense == "<=":
            model.add_constraint(left <= right)
        elif sense == ">=":
            model.add_constraint(left >= right)
        else:
            model.add_constraint(left == right)

    for t in range(1, T - 1):
        # Every cell shows exactly one tile (or is the empty cell).
        for c in cells:
            post(expr([holds[t, c, v] for v in tiles if (t, c, v) in holds]), "==", expr([1]))
        # There is exactly one empty cell.
        post(expr([blank(t, c) for c in cells]), "==", expr([1]))
        # Sliding never adds or removes a tile, so the tile numbers on the board keep their total.
        post(expr([x[t, c] for c in cells]), "==", expr([sum(tiles)]))

    for t in range(T - 1):
        for c in cells:
            # The empty cell moves to a neighbouring cell at every step: the board must change,
            # and only the tile next to the empty cell can slide into it.
            if (t + 1, c, 0) in holds:
                post(blank(t + 1, c), "<=", expr([blank(t, r) for r in neighbours(c)]))
            # Only the tile sliding into the empty cell moves: a cell that is empty neither before
            # nor after the step keeps its tile. Together with the constant total above, the cell
            # the empty space leaves receives exactly the tile that slid, so every board holds
            # each tile once.
            changing = blank(t, c) + blank(t + 1, c)
            if changing.is_constant() and changing.constant == 0:
                post(x[t + 1, c], "==", x[t, c])
            else:
                post(x[t + 1, c] - x[t, c], "<=", M * changing)
                post(x[t, c] - x[t + 1, c], "<=", M * changing)

    if impossible:
        # The given start and end cannot be joined in N_STEPS boards.
        flag = model.binary_var(name="impossible")
        model.add_constraint(flag == 1)
        model.add_constraint(flag == 0)

    steps = []
    for t in range(T):
        board = []
        for i in range(dim):
            row = []
            for j in range(dim):
                e = x[t, (i, j)]
                row.append(int(e.constant) if e.is_constant() else e)
            board.append(row)
        steps.append(board)
    return model, {"steps": steps}
