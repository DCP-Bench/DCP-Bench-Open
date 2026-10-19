# Hidato puzzle: fill an R x C grid with the numbers 1..R*C so that each number
# appears once, the given numbers stay where they are, and consecutive numbers
# touch horizontally, vertically or diagonally. The solved grid is output as x.
import mip


OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def neighbours(i, j, rows, cols):
    for di, dj in OFFSETS:
        a, b = i + di, j + dj
        if 0 <= a < rows and 0 <= b < cols:
            yield a, b


def build(instance):
    puzzle = instance["puzzle"]
    rows = len(puzzle)
    cols = len(puzzle[0])
    n = rows * cols
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # p[i][j][k] = 1 when cell (i, j) holds the number k + 1
    p = [
        [
            [model.add_var(f"p_{i}_{j}_{k}", var_type=mip.BINARY) for k in range(n)]
            for j in range(cols)
        ]
        for i in range(rows)
    ]
    # x[i][j] is the number in cell (i, j), the declared output
    x = [
        [model.add_var(f"x_{i}_{j}", lb=1, ub=n, var_type=mip.INTEGER) for j in range(cols)]
        for i in range(rows)
    ]

    # Each cell holds exactly one number, and x is that number
    for i in range(rows):
        for j in range(cols):
            model += mip.xsum(p[i][j]) == 1
            model += x[i][j] == mip.xsum((k + 1) * p[i][j][k] for k in range(n))

    # Fill in the empty cells: the numbers already on the board stay where they are
    for i in range(rows):
        for j in range(cols):
            given = puzzle[i][j]
            if given != 0:
                model += p[i][j][given - 1] == 1

    # The numbers 1 to R*C each appear once on the board
    for k in range(n):
        model += mip.xsum(p[i][j][k] for i in range(rows) for j in range(cols)) == 1

    # The numbers must be in increasing order: consecutive numbers touch
    # horizontally, vertically, or diagonally
    for k in range(n - 1):
        for i in range(rows):
            for j in range(cols):
                touching = mip.xsum(p[a][b][k + 1] for a, b in neighbours(i, j, rows, cols))
                model += p[i][j][k] <= touching

    return model, {"x": x}
