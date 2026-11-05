#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob022/

# Data
num_work = 12  # Number of tasks (pieces of work)
num_shifts = 14  # Number of possible shifts
shifts = [
    [0, 1, 2],          # Shift 0 covers tasks 0, 1, 2
    [0, 1, 2, 3],       # Shift 1 covers tasks 0, 1, 2, 3
    [2, 3, 4, 5],       # Shift 2 covers tasks 2, 3, 4, 5
    [4, 5],             # Shift 3 covers tasks 4, 5
    [6, 7],             # Shift 4 covers tasks 6, 7
    [6, 7, 8],          # Shift 5 covers tasks 6, 7, 8
    [8, 9],             # Shift 6 covers tasks 8, 9
    [8, 9, 10],         # Shift 7 covers tasks 8, 9, 10
    [10, 11],           # Shift 8 covers tasks 10, 11
    [0, 4, 8],          # Shift 9 covers tasks 0, 4, 8
    [0, 5, 10],         # Shift 10 covers tasks 0, 5, 10
    [1, 6, 11],         # Shift 11 covers tasks 1, 6, 11
    [2, 7, 9],          # Shift 12 covers tasks 2, 7, 9
    [3, 6, 8]           # Shift 13 covers tasks 3, 6, 8
]
# End of data

import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# x[i] is a binary variable, 1 if shift 'i' is selected, 0 otherwise.
x = cp.boolvar(shape=num_shifts, name="x")

# Constraints
# Each task must be covered by exactly one selected shift (set partitioning).
for t in range(num_work):
    # For each task 't', find all shifts that cover it and sum their selection variables.
    covering_shifts = [x[i] for i in range(num_shifts) if t in shifts[i]]
    model += (cp.sum(covering_shifts) == 1)

# Objective
# Minimize the total number of shifts used.
model.minimize(cp.sum(x))

# Solve and print
model.solve()

solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMpy script