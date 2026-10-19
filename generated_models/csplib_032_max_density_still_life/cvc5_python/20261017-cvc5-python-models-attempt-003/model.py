# Max density still life (CSPLib 032): place live cells on an n x m active grid so
# that the configuration is stable under Conway's Game of Life and the number of
# live cells is maximised. Cells outside the active grid are dead.
# Encoding: one Boolean per active cell, neighbour counts as linear sums over If(.,1,0),
# the two rules as implications, and window caps implied by the rules (see below),
# solved under QF_LIA.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]

    # Active cells (1-based row i in 1..n, column j in 1..m) are Boolean variables.
    g = {(i, j): cz.Bool(f"g_{i}_{j}") for i in range(1, n + 1) for j in range(1, m + 1)}

    def active(i, j):
        return 1 <= i <= n and 1 <= j <= m

    def live_count(i, j):
        # Number of live active neighbours of cell (i, j), as a linear sum.
        terms = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if (di, dj) != (0, 0) and active(i + di, j + dj):
                    terms.append(cz.If(g[(i + di, j + dj)], 1, 0))
        return cz.Sum(terms) if terms else None

    constraints = []

    # A live cell must have exactly 2 or 3 live neighbors to remain alive.
    # A dead cell, including any dead cell just outside the active grid, must not have
    # exactly 3 live neighbors (otherwise it would become alive).
    # Cells outside the active grid are dead, so their rule is a plain "not exactly 3".
    for i in range(0, n + 2):
        for j in range(0, m + 2):
            c = live_count(i, j)
            if c is None:
                continue
            if active(i, j):
                constraints.append(cz.Implies(g[(i, j)], cz.Or(c == 2, c == 3)))
                constraints.append(cz.Implies(cz.Not(g[(i, j)]), c != 3))
            else:
                constraints.append(c != 3)

    # Window caps, implied by the two rules: a 3x3 window holds at most 6 live cells,
    # and a 2x3 or 3x2 window holds at most 4. Windows are taken inside the padded grid
    # rows 0..n+1, columns 0..m+1; cells outside the active grid count as dead.
    # Only windows with more active cells than the cap are added.
    def add_cap(rows, cols, cap):
        cells = [(i, j) for i in rows for j in cols if active(i, j)]
        if len(cells) > cap:
            constraints.append(cz.Sum([cz.If(g[c], 1, 0) for c in cells]) <= cap)

    for r in range(0, n):
        for c in range(0, m):
            add_cap(range(r, r + 3), range(c, c + 3), 6)
    for r in range(0, n + 1):
        for c in range(0, m):
            add_cap(range(r, r + 2), range(c, c + 3), 4)
    for r in range(0, n):
        for c in range(0, m + 1):
            add_cap(range(r, r + 3), range(c, c + 2), 4)

    # Objective: maximise the number of live cells in the active grid.
    cells = [[g[(i, j)] for j in range(1, m + 1)] for i in range(1, n + 1)]
    objective = cz.Sum([cz.If(g[(i, j)], 1, 0) for i in range(1, n + 1) for j in range(1, m + 1)])

    solver = cz.SolverFor("QF_LIA")
    solver.add(*constraints)
    return solver, {"grid": cells}, ("maximize", objective)
