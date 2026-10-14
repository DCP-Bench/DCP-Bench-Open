from pycsp3 import *

givens = data.input_grid
# grid[i][j] is the digit in row i and column j
grid = VarArray(size=[9, 9], dom=range(1, 10))

satisfy(
    # each row contains all the digits 1 to 9
    [AllDifferent(grid[i]) for i in range(9)],
    # each column contains all the digits 1 to 9
    [AllDifferent(grid[:, j]) for j in range(9)],
    # each 3x3 section contains all the digits 1 to 9
    [AllDifferent([grid[3 * bi + r][3 * bj + c] for r in range(3) for c in range(3)])
     for bi in range(3) for bj in range(3)],
    # the given digits keep their values
    [grid[i][j] == givens[i][j] for i in range(9) for j in range(9) if givens[i][j] != 0],
)
