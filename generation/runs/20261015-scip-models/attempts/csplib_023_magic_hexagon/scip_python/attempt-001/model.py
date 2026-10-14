# Magic hexagon: place the numbers 1..N in the 19 cells of a hexagon so that
# each of the 15 lines (rows and diagonals) sums to the magic constant.
from pyscipopt import Model, quicksum

# The cells A..S in reading order, as in the problem's hexagon layout:
#   row 1: A B C
#   row 2: D E F G
#   row 3: H I J K L
#   row 4: M N O P
#   row 5: Q R S
# The 15 lines are the 5 horizontal rows, the 5 lines running down-right and
# the 5 lines running down-left.
LINES = [
    # horizontal rows
    ("A", "B", "C"),
    ("D", "E", "F", "G"),
    ("H", "I", "J", "K", "L"),
    ("M", "N", "O", "P"),
    ("Q", "R", "S"),
    # down-right diagonals
    ("A", "E", "J", "O", "S"),
    ("B", "F", "K", "P"),
    ("C", "G", "L"),
    ("D", "I", "N", "R"),
    ("H", "M", "Q"),
    # down-left diagonals
    ("C", "F", "J", "N", "Q"),
    ("B", "E", "I", "M"),
    ("A", "D", "H"),
    ("G", "K", "O", "R"),
    ("L", "P", "S"),
]
CELLS = "ABCDEFGHIJKLMNOPQRS"


def build(instance):
    n = instance["NUM_CELLS"]  # the numbers used are 1..n
    magic = instance["MAGIC_SUM"]  # every line sums to this value

    m = Model()
    # b[c, v] = 1 if cell c holds the number v
    b = {(c, v): m.addVar(name=f"b_{c}_{v}", vtype="B")
         for c in CELLS for v in range(1, n + 1)}
    # each cell holds exactly one number
    for c in CELLS:
        m.addCons(quicksum(b[c, v] for v in range(1, n + 1)) == 1,
                  name=f"one_number_{c}")
    # the numbers 1..n are used once each: all-different
    for v in range(1, n + 1):
        m.addCons(quicksum(b[c, v] for c in CELLS) == 1,
                  name=f"all_different_{v}")

    # the value of each cell, from its one-hot encoding
    x = {c: quicksum(v * b[c, v] for v in range(1, n + 1)) for c in CELLS}

    # each of the 15 lines sums to the magic constant
    for line in LINES:
        # the sum of the cells on this line equals the magic constant
        m.addCons(quicksum(x[c] for c in line) == magic,
                  name="line_" + "".join(line))

    # the output is the 19 cell values in the order A..S
    return m, {"LD": [x[c] for c in CELLS]}
