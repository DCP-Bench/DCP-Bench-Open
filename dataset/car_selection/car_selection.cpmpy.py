#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/car_selection

"""
This problem aims to assign participants to cars to maximize the total number of assignments.
Each participant may be interested in a subset of available cars. The problem ensures that each participant is assigned to at most one car, and each car is assigned to at most one participant.

Print the assignment matrix (assignments) as a list of lists of booleans, where assignments[i][j] is 1 if participant i is assigned to car j, and 0 otherwise.
"""

# Data

possible_assignments = [
        [1, 0, 1, 0, 0], # possible_assignments[i][j] is 1 if participant i is interested in car j, 0 otherwise
        [0, 0, 1, 1, 0],
        [1, 1, 1, 0, 1],
        [0, 1, 0, 1, 1],
        [1, 0, 0, 1, 0]
    ]

# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
possible_assignments = cpm_array(possible_assignments)
num_participants = len(possible_assignments)
num_cars = len(possible_assignments[0])

# Decision variables
assignments = boolvar(shape=(num_participants, num_cars), name="assignments")

# Model
model = Model()

# Constraint 1: Available Assignments
model += assignments <= possible_assignments

# Constraint 2: Each participant is assigned to at most one car
for i in range(num_participants):
    model += sum(assignments[i, :]) <= 1

# Constraint 3: Each car is assigned to at most one participant
for j in range(num_cars):
    model += sum(assignments[:, j]) <= 1

# Objective: Maximize the total number of assignments
model.maximize(sum(assignments))

# Solve the model
model.solve()

# Print the solution
solution = {
    "assignments": assignments.value().tolist()
}
print(json.dumps(solution))

# End of CPMPy script