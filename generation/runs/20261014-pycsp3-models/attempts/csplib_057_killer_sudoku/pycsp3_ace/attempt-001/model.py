from pycsp3 import *

# Killer sudoku on a 9 by 9 grid: fill the grid with the digits 1 to 9 so that each
# row, column and nonet holds every digit once, and each cage holds distinct digits
# that add up to the sum printed for the cage.

n = data.n
cages = data.problem  # each cage is [sum, [[row, column], ...]], counted from 1

# x[i][j] is the digit in row i, column j
x = VarArray(size=[n, n], dom=range(1, n + 1))

satisfy(
    # each row contains each digit exactly once
    [AllDifferent(x[i]) for i in range(n)],

    # each column contains each digit exactly once
    [AllDifferent(x[:, j]) for j in range(n)],

    # each nonet (3 by 3 block) contains each digit exactly once
    [AllDifferent([x[3 * a + r][3 * b + c] for r in range(3) for c in range(3)])
     for a in range(3) for b in range(3)],

    # no number appears more than once in a cage
    [AllDifferent([x[r - 1][c - 1] for (r, c) in cells]) for (_, cells) in cages],

    # the sum of all the numbers in a cage matches the sum printed in its corner
    [Sum(x[r - 1][c - 1] for (r, c) in cells) == total for (total, cells) in cages],
)
