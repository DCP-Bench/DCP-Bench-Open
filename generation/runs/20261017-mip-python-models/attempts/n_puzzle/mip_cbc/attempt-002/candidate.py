# N-puzzle: a grid with one empty cell and tiles 1..n*n-1 that move by sliding into the empty cell.
# Trace the steps from the start state to the end state, as N_STEPS board states including the
# start and the end. Freezing is not allowed: the state changes at each step.
# Formulation: a blank-position encoding. Each step moves the empty cell to a neighbouring cell, and
# the tile that was there slides into the old empty cell; every other tile stays where it is.
import mip


def build(instance):
    N = instance["N_STEPS"]
    start = instance["puzzle_start"]
    goal = instance["puzzle_end"]
    R = len(start)
    C = len(start[0])
    K = R * C  # tile values 0..K-1, where 0 is the empty cell
    cells = [(r, c) for r in range(R) for c in range(C)]

    def neighbours(cell):
        r, c = cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < R and 0 <= cc < C:
                yield (rr, cc)

    def position(board):
        pos = {}
        for r in range(R):
            for c in range(C):
                pos[board[r][c]] = (r, c)
        return pos

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    posS = position(start)
    posG = position(goal)
    blank_colour = (posS[0][0] + posS[0][1]) % 2

    # A tile moves at most one cell per step, so after t steps it lies within t cells of its start
    # cell and within N-1-t cells of its end cell. The empty cell also alternates colour on the grid.
    def allowed(t, cell, v):
        if dist(cell, posS[v]) > t or dist(cell, posG[v]) > N - 1 - t:
            return False
        if v == 0 and (cell[0] + cell[1] - blank_colour - t) % 2 != 0:
            return False
        return True

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # T[t, cell, v] = 1 when tile v (0 is the empty cell) is on cell at state t.
    T = {}
    for t in range(N):
        for cell in cells:
            for v in range(K):
                if allowed(t, cell, v):
                    T[t, cell, v] = m.add_var(name=f"T_{t}_{cell[0]}_{cell[1]}_{v}", var_type=mip.BINARY)

    def get(t, cell, v):
        return T.get((t, cell, v))

    # Each step moves the empty cell along one edge: A[t, p, q] = 1 when the empty cell goes from p to q
    # between states t and t+1.
    arcs = [(p, q) for p in cells for q in neighbours(p)]
    A = {}
    for t in range(N - 1):
        for p, q in arcs:
            if get(t, p, 0) is not None and get(t + 1, q, 0) is not None:
                A[t, p, q] = m.add_var(name=f"A_{t}_{p[0]}_{p[1]}_{q[0]}_{q[1]}", var_type=mip.BINARY)

    # Each step is one move of the empty cell to a neighbouring cell.
    for t in range(N - 1):
        moves = [A[t, p, q] for p, q in arcs if (t, p, q) in A]
        m.add_constr(mip.xsum(moves) == 1)
        for p, q in arcs:
            if (t, p, q) in A:
                # the empty cell must be at p in state t and at q in state t+1
                m.add_constr(A[t, p, q] <= get(t, p, 0))
                m.add_constr(A[t, p, q] <= get(t + 1, q, 0))

    # The tile on the target cell q slides into the empty cell p: when move p->q is made,
    # the content of p in state t+1 equals the content of q in state t.
    for t in range(N - 1):
        for p, q in arcs:
            if (t, p, q) not in A:
                continue
            a = A[t, p, q]
            for v in range(K):
                x0 = get(t, q, v)
                x1 = get(t + 1, p, v)
                if x0 is None and x1 is None:
                    continue
                if x0 is None:
                    m.add_constr(x1 + a <= 1)
                elif x1 is None:
                    m.add_constr(x0 + a <= 1)
                else:
                    m.add_constr(x1 - x0 + a <= 1)
                    m.add_constr(x0 - x1 + a <= 1)

    # A tile stays on its cell unless the empty cell enters or leaves that cell in this step.
    for t in range(N - 1):
        for cell in cells:
            touching = [A[t, p, q] for p, q in arcs if (t, p, q) in A and cell in (p, q)]
            L = mip.xsum(touching)
            for v in range(K):
                x0 = get(t, cell, v)
                x1 = get(t + 1, cell, v)
                if x0 is None and x1 is None:
                    continue
                d = mip.xsum([x1] if x1 is not None else []) - mip.xsum([x0] if x0 is not None else [])
                m.add_constr(d - L <= 0)
                m.add_constr(-d - L <= 0)

    # Each state puts exactly one tile on each cell, and each tile sits on exactly one cell.
    for t in range(N):
        for cell in cells:
            m.add_constr(mip.xsum([T[t, cell, v] for v in range(K) if (t, cell, v) in T]) == 1)
        for v in range(K):
            m.add_constr(mip.xsum([T[t, cell, v] for cell in cells if (t, cell, v) in T]) == 1)

    # The steps are the board states, one R x C matrix per step, each entry the tile value on that cell.
    steps = []
    for t in range(N):
        board = []
        for r in range(R):
            row = []
            for c in range(C):
                terms = [v * T[t, (r, c), v] for v in range(1, K) if (t, (r, c), v) in T]
                row.append(mip.xsum(terms) if terms else 0)
            board.append(row)
        steps.append(board)

    return m, {"steps": steps}
