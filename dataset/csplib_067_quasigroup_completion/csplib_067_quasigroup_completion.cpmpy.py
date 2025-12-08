#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob067/
# Source model: https://www.csplib.org/Problems/prob067/models/QuasigroupCompletion.mzn.html

"""
An order m quasigroup is a Latin square of size m. That is, an m x m
multiplication table in which each element from 1 to m occurs exactly once
in every row and every column. This problem asks to complete a partially
filled quasigroup.

Print the completed quasigroup (puzzle).
"""

# Data
# The size of the quasigroup (Latin square).
N = 5
# The initial board configuration. 0 represents an empty cell to be filled.
# The numbers to fill are in the range [1, N].
start = [[1, 0, 0, 0, 0],
         [0, 2, 0, 0, 0],
         [0, 0, 3, 0, 0],
         [0, 0, 0, 4, 0],
         [0, 0, 0, 0, 5]]
# End of data

# Import libraries
import cpmpy as cp
import json
import numpy as np

# Model definition
model = cp.Model()

# Decision Variables
# The puzzle grid, with values from 1 to N.
puzzle = cp.intvar(1, N, shape=(N, N), name="puzzle")

# Constraints
# 1. Pre-fill the grid with the starting values.
# We iterate through the start matrix and add a constraint for each non-zero cell.
start_np = np.array(start)
for i in range(N):
    for j in range(N):
        if start_np[i, j] != 0:
            model += puzzle[i, j] == start_np[i, j]

# 2. Each row must contain unique values from 1 to N.
for i in range(N):
    model += cp.AllDifferent(puzzle[i, :])

# 3. Each column must contain unique values from 1 to N.
for j in range(N):
    model += cp.AllDifferent(puzzle[:, j])


# Solve and print
# This is a satisfaction problem, so we just need to find one solution.
if model.solve():
    solution = {"puzzle": puzzle.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")