# Max density still life (CSPLib 032): place live cells on an n x m active grid so
# that the configuration is stable under Conway's Game of Life and the number of
# live cells is maximised. Cells outside the active grid are dead.
# Encoding: each cell is an integer 0/1 variable and the neighbour counts are linear
# sums; the two rules are linear inequalities with a big-M constant, and the
# "not exactly 3" rule is a disjunction over linear bounds.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]

    rows = n + 2
    cols = m + 2
    x = [[cz.Int(f"x_{i}_{j}") for j in range(cols)] for i in range(rows)]

    constraints = []

    # Every cell is 0 or 1.
    for i in range(rows):
        for j in range(cols):
            constraints.append(x[i][j] >= 0)
            constraints.append(x[i][j] <= 1)

    # The border around the active grid is outside the active grid, so it is dead.
    for i in range(rows):
        for j in range(cols):
            if i in (0, rows - 1) or j in (0, cols - 1):
                constraints.append(x[i][j] == 0)

    # Number of live neighbours of every padded cell, as a linear sum.
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
                        terms.append(x[a][b])
            count[(i, j)] = cz.Sum(terms)

    # A live cell must have exactly 2 or 3 live neighbors to remain alive.
    # Live (x = 1): 2 <= count <= 3. The big-M term 5 relaxes the upper bound when dead.
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = count[(i, j)]
            constraints.append(c >= 2 * x[i][j])
            constraints.append(c <= 3 + 5 * (1 - x[i][j]))

    # A dead cell, including any dead cell just outside the active grid, must not have
    # exactly 3 live neighbors (otherwise it would become alive).
    # Dead (x = 0): count <= 2 or count >= 4.
    for i in range(rows):
        for j in range(cols):
            c = count[(i, j)]
            constraints.append(cz.Or(x[i][j] == 1, c <= 2, c >= 4))

    # The active grid is the n x m block inside the border.
    cells = [[x[i][j] == 1 for j in range(1, m + 1)] for i in range(1, n + 1)]
    objective = cz.Sum([x[i][j] for i in range(1, n + 1) for j in range(1, m + 1)])

    return constraints, {"grid": cells}, ("maximize", objective)
