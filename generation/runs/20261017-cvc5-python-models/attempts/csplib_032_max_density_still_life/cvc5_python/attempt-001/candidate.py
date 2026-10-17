# Max density still life (CSPLib 032): place live cells on an n x m active grid so
# that the configuration is stable under Conway's Game of Life and the number of
# live cells is maximised. Cells outside the active grid are dead.
# The grid is padded with one dead border row and column on each side, so the dead
# cells just outside the active grid are checked by the same rule as the inner cells.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]

    rows = n + 2
    cols = m + 2
    g = [[cz.Bool(f"g_{i}_{j}") for j in range(cols)] for i in range(rows)]

    constraints = []

    # The border around the active grid is outside the active grid, so it is dead.
    # Cells outside the padded board have no state and count as dead.
    for i in range(rows):
        for j in range(cols):
            if i in (0, rows - 1) or j in (0, cols - 1):
                constraints.append(cz.Not(g[i][j]))

    # Number of live neighbours of every padded cell.
    count = {}
    for i in range(rows):
        for j in range(cols):
            terms = []
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    a, b = i + di, j + dj
                    if 0 <= a < rows and 0 <= b < cols:
                        terms.append(cz.If(g[a][b], 1, 0))
            count[(i, j)] = cz.Sum(terms)

    # A live cell must have exactly 2 or 3 live neighbors to remain alive.
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = count[(i, j)]
            constraints.append(cz.Implies(g[i][j], cz.Or(c == 2, c == 3)))

    # A dead cell, including any dead cell just outside the active grid, must not have
    # exactly 3 live neighbors (otherwise it would become alive).
    for i in range(rows):
        for j in range(cols):
            constraints.append(cz.Implies(cz.Not(g[i][j]), count[(i, j)] != 3))

    # The active grid is the n x m block inside the border.
    cells = [[g[i][j] for j in range(1, m + 1)] for i in range(1, n + 1)]
    live = [cz.If(g[i][j], 1, 0) for i in range(1, n + 1) for j in range(1, m + 1)]
    objective = cz.Sum(live)

    return constraints, {"grid": cells}, ("maximize", objective)
