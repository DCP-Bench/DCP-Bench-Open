# Magic hexagon: place the numbers 1 to NUM_CELLS in the 19 cells A..S of a
# hexagon so that each of the 15 lines (rows and diagonals) sums to MAGIC_SUM.
#
# Encoding: one-hot Bools x_<cell>_<value>. Each cell holds exactly one value and
# each value sits in exactly one cell. A cell's number is the integer expression
# sum(v * x_<cell>_<v>), which is used in the line sums and in the output LD.
from paramita.modelling import Bool

# Cells in reading order: row 1 A B C, row 2 D E F G, row 3 H I J K L,
# row 4 M N O P, row 5 Q R S.
CELLS = list("ABCDEFGHIJKLMNOPQRS")

# The 15 lines of the hexagon: 5 horizontal rows, then 5 lines in each of the two
# diagonal directions. The lines come from the hexagon's layout, which the
# problem fixes, so they are not read from the instance.
LINES = [
    "ABC", "DEFG", "HIJKL", "MNOP", "QRS",   # rows
    "HMQ", "DINR", "AEJOS", "BFKP", "CGL",   # one diagonal direction
    "ADH", "BEIM", "CFJNQ", "GKOR", "LPS",   # the other diagonal direction
]


def build(instance):
    # Domain and magic constant come from the instance.
    n = instance["NUM_CELLS"]
    magic = instance["MAGIC_SUM"]
    dom = range(1, n + 1)
    idx = {c: i for i, c in enumerate(CELLS)}

    x = {c: {v: Bool(f"x_{c}_{v}") for v in dom} for c in CELLS}
    cons = []

    # every cell holds exactly one number
    for c in CELLS:
        cons.append(sum(x[c].values()) == 1)

    # every number from 1 to NUM_CELLS is used in exactly one cell
    for v in dom:
        cons.append(sum(x[c][v] for c in CELLS) == 1)

    # the number in each cell, as an integer expression
    val = {c: sum(v * x[c][v] for v in dom) for c in CELLS}

    # each of the 15 lines sums to the magic constant
    for line in LINES:
        cons.append(sum(val[c] for c in line) == magic)

    outputs = {"LD": [val[c] for c in CELLS]}
    return cons, outputs
