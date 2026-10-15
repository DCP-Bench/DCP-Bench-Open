# Kakuro: fill the white cells with digits 1 to 9 so that each entry sums to its clue
# and no digit is repeated within an entry.
from paramita.modelling import Bool

DIGITS = range(1, 10)


def build(instance):
    n = instance["n"]
    # the instance lists the black and clue cells (1-based); every other cell of the grid is white
    black = {tuple(cell) for cell in instance["blanks"]}
    white = [(r, c) for r in range(1, n + 1) for c in range(1, n + 1) if (r, c) not in black]
    # entries: [clue, [r, c], [r, c], ...]; across and down entries share one list
    entries = instance["problem"]

    # one-hot encoding: xv[cell][v] is true when the white cell holds digit v
    xv = {cell: {v: Bool(f"x_{cell[0]}_{cell[1]}_{v}") for v in DIGITS} for cell in white}

    cons = []

    # each white cell holds exactly one digit from 1 to 9
    for cell in white:
        cons.append(sum(xv[cell].values()) == 1)

    for clue, *cells in entries:
        cells = [tuple(cell) for cell in cells]

        # no digit is duplicated in any entry
        for v in DIGITS:
            cons.append(sum(xv[cell][v] for cell in cells) <= 1)

        # the digits in each entry add up to its clue
        cons.append(sum(v * xv[cell][v] for cell in cells for v in DIGITS) == clue)

    # solution matrix: the digit in each white cell, 0 on black and clue cells
    x = []
    for r in range(1, n + 1):
        row = []
        for c in range(1, n + 1):
            if (r, c) in xv:  # a white cell
                row.append(sum(v * xv[(r, c)][v] for v in DIGITS))
            else:
                row.append(0)
        x.append(row)

    return cons, {"x": x}
