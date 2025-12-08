#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/flow_free_game.py
# Source description: https://www.bigduckgames.com/flowfree

"""
Connect matching colors with pipe to create a flow. Pair all colors, and cover the
entire board to solve each puzzle in Flow Free. But watch out, pipes will break if
they cross or overlap! For this problem instance, we have a 5x5 board with the
following configuration:

1, 0, 0, 2, 3
0, 0, 0, 4, 0
0, 0, 4, 0, 0
0, 2, 3, 0, 5
0, 1, 5, 0, 0

The cells with a value of 0 are empty and need to be filled with a color.

Print the board (B) as a list of lists, where each cell value is the color of the cell as an integer from 1 to 5.
"""

# Data
# board[i][j] is the color of the cell at row i and column j, or 0 if the cell needs to be filled
board = [[1, 0, 0, 2, 3],
         [0, 0, 0, 4, 0],
         [0, 0, 4, 0, 0],
         [0, 2, 3, 0, 5],
         [0, 1, 5, 0, 0]]
# End of data

# Import libraries
from cpmpy import *
import json

M = len(board)
N = len(board[0])
B = intvar(1, 10, shape=(M, N), name="B")

model = Model()

for i in range(M):
    for j in range(N):
        same_neighs_ij = sum([B[i][j] == B[k][l]
                              for k in range(M) for l in range(N) if abs(k - i) + abs(l - j) == 1])
        if board[i][j] != 0:
            model += [B[i, j] == board[i][j]]
            model += [same_neighs_ij == 1]
        else:
            model += [(same_neighs_ij == 2) | (B[i][j] == 0)]

model.solve()

solution = {"B": B.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
