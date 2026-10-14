from pycsp3 import *

board = data.game_data
size = len(board)
# mines[i][j] is 1 when the cell has a mine
mines = VarArray(size=[size, size], dom={0, 1})

neighbours = lambda i, j: [(i + di, j + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1)
                           if (di, dj) != (0, 0) and 0 <= i + di < size and 0 <= j + dj < size]

satisfy(
    # an opened cell shows a number, and it has no mine
    [mines[i][j] == 0 for i in range(size) for j in range(size) if board[i][j] != data.X],
    # the number on an opened cell is the number of mines among its adjacent cells
    [Sum(mines[a][b] for a, b in neighbours(i, j)) == board[i][j]
     for i in range(size) for j in range(size) if board[i][j] != data.X],
)
