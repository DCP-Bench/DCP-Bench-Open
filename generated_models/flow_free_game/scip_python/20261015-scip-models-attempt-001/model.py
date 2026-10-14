# Flow Free: colour every cell of the board so that each colour forms one pipe joining
# its two endpoints, pipes do not cross or overlap, and the whole board is covered.
from pyscipopt import Model, quicksum


def build(instance):
    board = instance["board"]
    n_rows = len(board)
    n_cols = len(board[0])
    n_cells = n_rows * n_cols
    colors = sorted({v for row in board for v in row if v != 0})
    cells = [(i, j) for i in range(n_rows) for j in range(n_cols)]

    def nbrs(p):
        i, j = p
        out = []
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= i + di < n_rows and 0 <= j + dj < n_cols:
                out.append((i + di, j + dj))
        return out

    m = Model()

    # x[p, c] = 1 if cell p has colour c
    x = {(p, c): m.addVar(name=f"x[{p[0]},{p[1]},{c}]", vtype="B") for p in cells for c in colors}

    # every cell has exactly one colour, and the board is covered
    for p in cells:
        m.addCons(quicksum(x[p, c] for c in colors) == 1)

    # the numbered cells of the board keep their colour
    endpoints = {}
    for p in cells:
        i, j = p
        if board[i][j] != 0:
            c = board[i][j]
            m.addCons(x[p, c] == 1)
            endpoints.setdefault(c, []).append(p)

    # a pipe is a path: each endpoint has one neighbour of its colour,
    # and every other cell of a colour has exactly two neighbours of that colour
    for p in cells:
        i, j = p
        for c in colors:
            same = quicksum(x[q, c] for q in nbrs(p))
            if board[i][j] == c:
                m.addCons(same == 1)
            elif board[i][j] == 0:
                m.addConsIndicator(same <= 2, binvar=x[p, c])
                m.addConsIndicator(same >= 2, binvar=x[p, c])

    # a pipe is connected: a unit of flow leaves the first endpoint of each colour and
    # every other cell of that colour absorbs one unit, along pipe cells only.
    # Cycles that do not reach an endpoint cannot absorb flow, so they are excluded.
    flow = {}
    for c in colors:
        for p in cells:
            for q in nbrs(p):
                f = m.addVar(name=f"flow[{c},{p[0]},{p[1]},{q[0]},{q[1]}]", vtype="C", lb=0, ub=n_cells)
                flow[c, p, q] = f
                m.addCons(f <= n_cells * x[p, c])
                m.addCons(f <= n_cells * x[q, c])
        for p in cells:
            if p == endpoints[c][0]:
                continue
            # the cell of colour c absorbs one unit of flow
            m.addCons(
                quicksum(flow[c, q, p] for q in nbrs(p)) - quicksum(flow[c, p, q] for q in nbrs(p))
                == x[p, c]
            )

    # the output B gives the colour of each cell
    B = [[quicksum(c * x[(i, j), c] for c in colors) for j in range(n_cols)] for i in range(n_rows)]
    return m, {"B": B}
