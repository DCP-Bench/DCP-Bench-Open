from pycsp3 import *

puzzle = data.puzzle
R = len(puzzle)
C = len(puzzle[0])
N = R * C  # the numbers run from 1 to the number of cells

# the cells, numbered row by row; the value 0 in the puzzle marks an empty cell
cells = VarArray(size=R * C, dom=range(1, N + 1))
# the solved grid, as rows of the cells
x = [[cells[i * C + j] for j in range(C)] for i in range(R)]

satisfy(
    # every number from 1 to N is used once
    AllDifferent(cells),
    # the numbers given in the puzzle keep their places
    [cells[i * C + j] == puzzle[i][j] for i in range(R) for j in range(C) if puzzle[i][j] != 0],
)

# for each number, the row, the column and the position of its cell
rows_of = VarArray(size=N, dom=range(R))
cols_of = VarArray(size=N, dom=range(C))
where = VarArray(size=N, dom=range(R * C))
satisfy(
    # the position of a number is its row times the number of columns plus its column
    [where[k] == rows_of[k] * C + cols_of[k] for k in range(N)],
    # the cell at the position of a number holds that number
    [cells[where[k]] == k + 1 for k in range(N)],
)

# consecutive numbers touch horizontally, vertically or diagonally
satisfy(
    [abs(rows_of[k] - rows_of[k + 1]) <= 1 for k in range(N - 1)],
    [abs(cols_of[k] - cols_of[k + 1]) <= 1 for k in range(N - 1)],
)
