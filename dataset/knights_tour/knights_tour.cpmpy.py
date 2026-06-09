#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/knights_tour_circuit.py

"""
A knight's tour is a sequence of moves of a knight on a chessboard such that the knight visits every
square exactly once (without returning to the starting square).
The objective is to find a knight's tour on a chessboard.
The tour is represented by integers from 0 to n*n-1, where n is the size of the chessboard.

Print the chessboard (x) as a list of lists of integers from 0 to n*n-1, where each integer represents the move number of the knight.
"""

import numpy as np
from cpmpy import *
import json

# Data
n = 6  # Size of the chessboard (must be even)
# End of data

import cpmpy as cp
import json

model = cp.Model()

# Variables
x = intvar(0, n * n - 1, shape=(n, n), name="x")

# Constraints
model += cp.AllDifferent(x)  # Each square must be visited exactly once

# Knight's moves
knight_moves = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2)
]

# Add constraints for knight's moves
for i in range(n):
    for j in range(n):
        current_pos = x[i, j]
        possible_next_positions = [[i + move[0], j + move[1]] for move in knight_moves if 0 <= i + move[0] < n and 0 <= j + move[1] < n]
        next_positions = [x[pos[0], pos[1]] for pos in possible_next_positions]
        model += (current_pos != n*n-1).implies(cp.Count(next_positions, current_pos + 1) == 1)  # Exactly one knight move to the next position
        model += (current_pos != 0).implies(cp.Count(next_positions, current_pos - 1) == 1)  # Exactly one knight move from the previous position


# Solve the model
model.solve()

solution = {
    'x': x.value().tolist()
}
print(json.dumps(solution, indent=4))
# End of CPMPy Model
