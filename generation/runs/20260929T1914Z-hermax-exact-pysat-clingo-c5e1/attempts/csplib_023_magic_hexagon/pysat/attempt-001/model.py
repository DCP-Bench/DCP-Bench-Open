# Magic hexagon: place the numbers 1..19 in the 19 cells of a hexagon (rows of
# 3, 4, 5, 4, 3 cells) so that the numbers along each of the 15 lines add up to
# the same magic sum.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

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

    pool = IDPool()
    # LD[c] = the number in cell c; direct encoding, one literal per number
    LD = [Integer(f"LD_{c}", 1, n_cells, vpool=pool) for c in range(n_cells)]
    engine = IntegerEngine(vars=LD, vpool=pool)

    # every number from 1 to 19 is used exactly once
    engine.add_alldifferent(LD)

    # every line of the hexagon adds up to the magic sum
    for line in LINES:
        engine.add_linear(sum(LD[c] for c in line) == magic_sum)

    return engine.clausify(), {"LD": LD}
