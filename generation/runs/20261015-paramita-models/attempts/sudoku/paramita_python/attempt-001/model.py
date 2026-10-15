# Sudoku on a 9x9 grid, digits 1..9, one-hot encoding per cell.
# x[r][c][v] is true when cell (r, c) holds digit v.
from paramita.modelling import Bool, If

N = 9
BOX = 3
DIGITS = range(1, N + 1)


def build(instance):
    clues = instance["input_grid"]

    # one-hot Bools: x[r][c][v] = cell (r, c) holds digit v
    x = [[{v: Bool(f"x_{r}_{c}_{v}") for v in DIGITS} for c in range(N)] for r in range(N)]

    cons = []

    # every cell holds exactly one digit
    for r in range(N):
        for c in range(N):
            cons.append(sum(x[r][c].values()) == 1)

    # every row contains each digit exactly once
    for r in range(N):
        for v in DIGITS:
            cons.append(sum(x[r][c][v] for c in range(N)) == 1)

    # every column contains each digit exactly once
    for c in range(N):
        for v in DIGITS:
            cons.append(sum(x[r][c][v] for r in range(N)) == 1)

    # every 3x3 section contains each digit exactly once
    for br in range(0, N, BOX):
        for bc in range(0, N, BOX):
            for v in DIGITS:
                cons.append(
                    sum(x[br + i][bc + j][v] for i in range(BOX) for j in range(BOX)) == 1
                )

    # the given cells of the input grid keep their digits (0 = empty)
    for r in range(N):
        for c in range(N):
            v = clues[r][c]
            if v != 0:
                cons.append(x[r][c][v])

    # the solved grid, each cell as an integer expression over its one-hot digits
    grid = [[sum(v * x[r][c][v] for v in DIGITS) for c in range(N)] for r in range(N)]

    return cons, {"grid": grid}
