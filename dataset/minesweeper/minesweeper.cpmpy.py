#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/minesweeper.py
# Source description: https://minesweeper.online

"""
Minesweeper rules are very simple. The board is divided into cells, with mines randomly distributed. To win,
you need to open all the cells. The number on a cell shows the number of mines adjacent to it. Using this
information, you can determine cells that are safe, and cells that contain mines. Cells suspected of being mines can
be marked with a flag using the right mouse button.

The task is to determine which 'X' fields contain mines based on the provided numerical clues.

Print whether each cell is a mine or not (mines) as a list of lists of booleans, where True indicates a mine and False indicates no mine.
"""

# Data
X = -1
game_data = [  # 0-8: number of mines around, -1: not opened
    [2, 3, X, 2, 2, X, 2, 1],
    [X, X, 4, X, X, 4, X, 2],
    [X, X, X, X, X, X, 4, X],
    [X, 5, X, 6, X, X, X, 2],
    [2, X, X, X, 5, 5, X, 2],
    [1, 3, 4, X, X, X, 4, X],
    [0, 1, X, 4, X, X, X, 3],
    [0, 1, 2, X, 2, 3, X, 2]
]
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json

# Parameters
game = np.array(game_data)
rows, cols = game.shape
S = [-1, 0, 1]  # for the neighbors of a cell

# Decision Variables
mines = boolvar(shape=game.shape)  # True: mine, False: not mine

model = Model()
for (r, c), val in np.ndenumerate(game):
    if val != X:
        # This cell cannot be a mine
        model += mines[r, c] == 0
        # Count neighbors
        model += (sum(mines[r + a, c + b]
                      for a in S for b in S
                      if 0 <= r + a < rows and 0 <= c + b < cols and (a, b) != (0, 0))
                  == val)

# Solve
model.solve()

# Print
solution = {"mines": mines.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
