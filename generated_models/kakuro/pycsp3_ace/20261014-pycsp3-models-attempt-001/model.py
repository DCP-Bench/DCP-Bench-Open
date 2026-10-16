from pycsp3 import *

# Kakuro: insert a digit from 1 to 9 into each white cell so that the digits of each clue add up to
# the clue, and no digit is repeated within a clue. Black cells hold 0. Cells are 1-based (row, column)
# in the instance; the white cells are the cells that some clue covers, the black cells are the blanks.
n = data.n
clues = data["problem"]
black_cells = [(r, c) for (r, c) in data.blanks]

# x[r][c] is the digit of cell (r, c) (0-based indices here), 0 for a black cell
x = VarArray(size=[n, n], dom=range(10))

satisfy(
    # every black cell holds 0
    [x[r - 1][c - 1] == 0 for (r, c) in black_cells],
    # every white cell holds a digit from 1 to 9
    [x[r - 1][c - 1] != 0 for clue in clues for (r, c) in clue[1:]],
    # the digits of each clue are different
    [AllDifferent([x[r - 1][c - 1] for (r, c) in clue[1:]]) for clue in clues],
    # the digits of each clue add up to the clue
    [Sum(x[r - 1][c - 1] for (r, c) in clue[1:]) == clue[0] for clue in clues],
)
