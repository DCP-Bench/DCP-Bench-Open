# Magic hexagon: place the numbers 1..19 in the 19 cells of a hexagon (rows of
# 3, 4, 5, 4, 3 cells) so that the numbers along each of the 15 lines add up to
# the same magic sum.
from pychoco.model import Model

# The geometry is fixed by the problem. Cells are numbered row by row:
#       0  1  2
#     3  4  5  6
#   7  8  9 10 11
#    12 13 14 15
#      16 17 18
LINES = [
    # the 5 horizontal rows
    [0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18],
    # the 5 diagonals running from top left to bottom right
    [0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18],
    # the 5 diagonals running from top right to bottom left
    [2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16],
]


def build(instance):
    n_cells = instance["NUM_CELLS"]
    magic_sum = instance["MAGIC_SUM"]

    model = Model()

    # LD[c] = the number in cell c
    LD = [model.intvar(1, n_cells, name=f"LD_{c}") for c in range(n_cells)]

    # every number from 1 to 19 is used exactly once
    model.all_different(LD).post()

    # every line of the hexagon adds up to the magic sum
    for line in LINES:
        model.sum([LD[c] for c in line], "=", magic_sum).post()

    return model, {"LD": LD}
