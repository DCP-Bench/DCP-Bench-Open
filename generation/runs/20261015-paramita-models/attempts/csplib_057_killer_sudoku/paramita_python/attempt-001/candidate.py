# Killer sudoku: fill a 9x9 grid with digits 1..9 so that rows, columns and
# nonets (3x3 boxes) each contain every digit once, every cage sums to its
# printed total, and no digit repeats inside a cage.
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # list of [total, [[row, col], ...]], 1-based cells
    box = 3
    values = range(1, n + 1)

    # xv[r][c][v] = 1 if cell (r, c) holds the digit v (one-hot encoding)
    xv = [[{v: Bool(f"x_{r}_{c}_{v}") for v in values} for c in range(n)] for r in range(n)]
    cons = []

    # each cell holds exactly one digit
    for r in range(n):
        for c in range(n):
            cons.append(sum(xv[r][c].values()) == 1)

    # each row contains each digit exactly once
    for r in range(n):
        for v in values:
            cons.append(sum(xv[r][c][v] for c in range(n)) == 1)

    # each column contains each digit exactly once
    for c in range(n):
        for v in values:
            cons.append(sum(xv[r][c][v] for r in range(n)) == 1)

    # each nonet (3x3 box) contains each digit exactly once
    for br in range(0, n, box):
        for bc in range(0, n, box):
            cells = [(br + dr, bc + dc) for dr in range(box) for dc in range(box)]
            for v in values:
                cons.append(sum(xv[r][c][v] for r, c in cells) == 1)

    # each cage sums to the total printed in its corner, and no digit repeats in a cage
    for total, cells in cages:
        cells = [(r - 1, c - 1) for r, c in cells]
        cons.append(sum(v * xv[r][c][v] for r, c in cells for v in values) == total)
        for v in values:
            cons.append(sum(xv[r][c][v] for r, c in cells) <= 1)

    x = [[sum(v * xv[r][c][v] for v in values) for c in range(n)] for r in range(n)]
    return cons, {"x": x}
