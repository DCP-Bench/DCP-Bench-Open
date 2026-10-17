# Flow Free game: colour every cell of a rectangular board so that each colour
# forms one pipe joining its two matching numbered cells, pipes do not cross or
# overlap, and the whole board is covered. Output B is the board of colours 1..K.
import mip


def build(instance):
    board = instance["board"]
    rows = len(board)
    cols = len(board[0])
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    n_cells = len(cells)
    palette = sorted({v for row in board for v in row if v != 0})

    def neighbours(p):
        r, c = p
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= r + dr < rows and 0 <= c + dc < cols:
                yield (r + dr, c + dc)

    # the two numbered cells of each colour; the first is the pipe's start, the second its end
    ends = {k: [p for p in cells if board[p[0]][p[1]] == k] for k in palette}
    for k in palette:
        assert len(ends[k]) == 2, "each colour must have exactly two numbered cells"

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # x[p, k] = 1 when cell p has colour k
    x = {}
    for p in cells:
        for k in palette:
            x[p, k] = model.add_var(name=f"x_{p[0]}_{p[1]}_{k}", var_type=mip.BINARY)

    # cover the entire board: every cell holds exactly one colour
    for p in cells:
        model.add_constr(mip.xsum(x[p, k] for k in palette) == 1)

    # the numbered cells keep their colour
    for p in cells:
        if board[p[0]][p[1]] != 0:
            model.add_constr(x[p, board[p[0]][p[1]]] == 1)

    # order[p] is a position along the pipe; it rules out loops that are not joined to the start
    order = {}
    for p in cells:
        order[p] = model.add_var(name=f"o_{p[0]}_{p[1]}", var_type=mip.INTEGER, lb=0, ub=n_cells - 1)

    # y[q, p, k] = 1 when the pipe of colour k runs from neighbouring cell q into cell p
    # (no arc enters the start cell of a colour)
    y = {}
    for k in palette:
        start = ends[k][0]
        for p in cells:
            if p == start:
                continue
            for q in neighbours(p):
                v = model.add_var(name=f"y_{q[0]}_{q[1]}_{p[0]}_{p[1]}_{k}", var_type=mip.BINARY)
                y[q, p, k] = v
                # a pipe piece exists only between two cells of its colour
                model.add_constr(v <= x[q, k])
                model.add_constr(v <= x[p, k])
                # a piece runs from an earlier cell to a later one, so the pipe has no loops
                model.add_constr(order[p] - order[q] - n_cells * v >= 1 - n_cells)

    # Connect matching colours with pipe: each colour's pipe is a single path from
    # its start cell to its end cell, with every other cell of that colour
    # linked to two neighbours and each end cell to one.
    for k in palette:
        start, end = ends[k]
        for p in cells:
            inc = [y[q, p, k] for q in neighbours(p) if (q, p, k) in y]
            out = [y[p, q, k] for q in neighbours(p) if (p, q, k) in y]
            if p == start:
                # the start cell has one pipe leaving it and none entering it
                model.add_constr(mip.xsum(out) == 1)
            elif p == end:
                # the end cell has one pipe entering it and no other pipe
                model.add_constr(mip.xsum(inc) == 1)
                model.add_constr(mip.xsum(inc + out) == 1)
            else:
                # a cell of colour k in the middle of a pipe has one pipe in and one out;
                # a cell without colour k has no pipe at all
                model.add_constr(mip.xsum(inc) == x[p, k])
                model.add_constr(mip.xsum(inc + out) == 2 * x[p, k])

    # B[r][c] is the colour of cell (r, c) as an integer 1..K
    lo, hi = min(palette), max(palette)
    B = [[None] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            p = (r, c)
            v = model.add_var(name=f"B_{r}_{c}", var_type=mip.INTEGER, lb=lo, ub=hi)
            model.add_constr(v == mip.xsum(k * x[p, k] for k in palette))
            B[r][c] = v

    return model, {"B": B}
