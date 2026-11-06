#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/flow_free_game.py
# Source description: https://www.bigduckgames.com/flowfree

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
