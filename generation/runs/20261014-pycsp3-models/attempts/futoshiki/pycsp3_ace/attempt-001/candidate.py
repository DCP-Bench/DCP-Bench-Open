# Futoshiki: fill an n by n grid with the digits 1 to n so that each row and each column holds every digit once, respecting the given digits and the inequalities.
from pycsp3 import *

values = data.values
lt = data.lt
n = len(values)

# grid[i][j] is the digit in row i and column j, 0-indexed
grid = VarArray(size=[n, n], dom=range(1, n + 1))

satisfy(
    # each row holds every digit once
    [AllDifferent(grid[i]) for i in range(n)],
    # each column holds every digit once
    [AllDifferent(grid[:, j]) for j in range(n)],
    # the given digits are fixed
    [grid[i][j] == values[i][j] for i in range(n) for j in range(n) if values[i][j] != 0],
    # the inequality clues: the first cell is lower than the second cell
    [grid[r1 - 1][c1 - 1] < grid[r2 - 1][c2 - 1] for (r1, c1, r2, c2) in lt],
)
