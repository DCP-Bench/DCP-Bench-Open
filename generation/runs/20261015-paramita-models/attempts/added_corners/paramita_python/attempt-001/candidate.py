# Added corners: enter the digits 1 through 8 in the circles and squares of the
# figure so that the number in each square is equal to the sum of the numbers in
# the adjoining circles. Print the values in reading order (left to right, top to
# bottom).
#
# The figure (problem constant, not an instance field):
#     C F C      C = circle, F = square
#     F   F
#     C F C
# Cells are numbered in reading order 0..7 (0 1 2 / 3 _ 4 / 5 6 7).
#
# Each cell's value is one-hot encoded: Bool "x_p_v" is true when cell p holds digit v.
from paramita.modelling import Bool

DIGITS = range(1, 9)   # the digits 1 through 8

# reading-order index -> (kind, figure row, figure column)
CELLS = [
    ("circle", 0, 0), ("square", 0, 1), ("circle", 0, 2),
    ("square", 1, 0), ("square", 1, 2),
    ("circle", 2, 0), ("square", 2, 1), ("circle", 2, 2),
]


# figure coordinates -> reading-order index
INDEX = {(r, c): p for p, (_, r, c) in enumerate(CELLS)}


def build(instance):
    n = len(CELLS)
    x = [{v: Bool(f"x_{p}_{v}") for v in DIGITS} for p in range(n)]
    value = [sum(v * x[p][v] for v in DIGITS) for p in range(n)]

    cons = []
    # every circle and square holds exactly one digit
    cons += [sum(x[p].values()) == 1 for p in range(n)]

    # the digits 1 through 8 are each used once
    cons += [sum(x[p][v] for p in range(n)) == 1 for v in DIGITS]

    # the number in each square is equal to the sum of the numbers in the adjoining circles:
    # a square adjoins the circles directly next to it in the figure
    for s, (kind, r, c) in enumerate(CELLS):
        if kind != "square":
            continue
        # the figure cells directly above, below, left and right of this square
        circles = [INDEX[(r + dr, c + dc)] for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0))
                   if (r + dr, c + dc) in INDEX and CELLS[INDEX[(r + dr, c + dc)]][0] == "circle"]
        cons += [value[s] == sum(value[q] for q in circles)]

    outputs = {"positions": value}
    return cons, outputs
