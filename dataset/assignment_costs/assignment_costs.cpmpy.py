#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/assignment.py
# Source description: Winston 'Operations Research', Assignment Problems, page 393f

# Data
cost = [  # Cost matrix, rows are tasks, columns are people
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]  # Cost matrix
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json

# Parameters
rows = len(cost)
cols = len(cost[0])

# Decision variables
max_cost = np.sum(np.array(cost))

total_cost = intvar(0, max_cost, name='cost')
x = boolvar(shape=(rows, cols), name="x")

model = Model(
    total_cost >= 0,
    total_cost == np.sum([x_row * cost_row for (x_row, cost_row) in zip(x, cost)]),

    # exacly one assignment per row, all rows (tasks) must be assigned.
    [sum(row) == 1 for row in x],

    # zero or one assignments per column (people)
    [sum(col) <= 1 for col in x.transpose()],
)

# Objective
model.minimize(total_cost)

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
