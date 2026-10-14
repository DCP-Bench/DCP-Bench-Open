from pycsp3 import *

# Minesweeper: find which unopened cells contain mines, given the numbers on the opened cells.
# The board is read from the instance: X marks an unopened cell, any other value is a clue.
X = data.X
clues = data.game_data
rows = len(clues)
cols = len(clues[0])

# mines[i][j] is 1 when cell (i, j) holds a mine, 0 when it does not
mines = VarArray(size=[rows, cols], dom={0, 1})

satisfy(
    # every cell either holds a mine or does not
    [mines[i][j] >= 0 for i in range(rows) for j in range(cols)],
    # an opened cell, which shows a number, holds no mine
    [mines[i][j] == 0 for i in range(rows) for j in range(cols) if clues[i][j] != X],
    # the number on an opened cell is the count of mines among its adjacent cells
    [Sum(mines[a][b] for a in range(max(0, i - 1), min(rows, i + 2))
         for b in range(max(0, j - 1), min(cols, j + 2)) if (a, b) != (i, j)) == clues[i][j]
     for i in range(rows) for j in range(cols) if clues[i][j] != X],
)
