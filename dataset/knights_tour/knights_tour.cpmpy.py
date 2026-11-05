#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/knights_tour_circuit.py

import numpy as np
from cpmpy import *
import json

# Data
n = 6  # Size of the chessboard
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
