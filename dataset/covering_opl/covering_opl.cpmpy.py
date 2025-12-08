#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/covering_opl.py
# Source description: This example is from the OPL example covering.mod

"""
Select a set of workers to perform all the tasks, while minimizing the cost. Each worker can perform certain tasks
and has a hiring cost. Ensure that all tasks are performed.

Print the total cost (total_cost) and whether each worker is selected (workers) as a list of booleans, where workers[i] is True if worker i is hired, and False otherwise.
"""

# Data
nb_workers = 32  # Number of workers
num_tasks = 15  # Number of tasks
Qualified = [  # Which worker is qualified for each task (1-based indexing)
    [1, 9, 19, 22, 25, 28, 31],
    [2, 12, 15, 19, 21, 23, 27, 29, 30, 31, 32],
    [3, 10, 19, 24, 26, 30, 32], [4, 21, 25, 28, 32],
    [5, 11, 16, 22, 23, 27, 31], [6, 20, 24, 26, 30, 32],
    [7, 12, 17, 25, 30, 31], [8, 17, 20, 22, 23],
    [9, 13, 14, 26, 29, 30, 31], [10, 21, 25, 31, 32],
    [14, 15, 18, 23, 24, 27, 30, 32], [18, 19, 22, 24, 26, 29, 31],
    [11, 20, 25, 28, 30, 32], [16, 19, 23, 31],
    [9, 18, 26, 28, 31, 32]]
Cost = [  # Cost of hiring each worker
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 6, 7, 8, 9
]
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
Workers = list(range(nb_workers))
Tasks = list(range(num_tasks))

#
# variables
#
workers = boolvar(shape=nb_workers, name="workers")  # 1 if the worker is hired, 0 otherwise
total_cost = intvar(0, nb_workers * sum(Cost), name="total_cost")  # Total cost of hiring the workers

model = Model(minimize=total_cost)

#
# constraints
#
model += [total_cost == sum(workers * Cost)]

for j in Tasks:
    # Sum the cost for hiring the qualified workers
    # (also, make 0-base)
    model += [sum([workers[c - 1] for c in Qualified[j]]) >= 1]

# Solve the model
model.solve()

# Print the solution
solution = {"total_cost": total_cost.value(), "workers": workers.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
