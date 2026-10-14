# Magic hexagon: place the numbers 1..19 in the 19 cells of a hexagon (rows of
# 3, 4, 5, 4, 3 cells) so that the numbers along each of the 15 lines add up to
# the same magic sum.
from exact import Exact

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
    values = range(1, n_cells + 1)

    solver = Exact()
    # LD[c] = the number in cell c
    LD = [f"LD_{c}" for c in range(n_cells)]
    # is_[c][v] is 1 exactly when cell c holds v; they make "every number used
    # once" a count of one cell per number
    is_ = [{} for _ in range(n_cells)]
    for c in range(n_cells):
        solver.addVariable(LD[c], 1, n_cells)
        for v in values:
            is_[c][v] = f"is_{c}_{v}"
            solver.addVariable(is_[c][v], 0, 1)
        solver.addConstraint([(1, is_[c][v]) for v in values], True, 1, True, 1)
        solver.addConstraint([(v, is_[c][v]) for v in values] + [(-1, LD[c])], True, 0, True, 0)

    # every number from 1 to 19 is used exactly once
    for v in values:
        solver.addConstraint([(1, is_[c][v]) for c in range(n_cells)], True, 1, True, 1)

    # every line of the hexagon adds up to the magic sum
    for line in LINES:
        solver.addConstraint([(1, LD[c]) for c in line], True, magic_sum, True, magic_sum)

    return solver, {"LD": LD}
