#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/rcpsp.py
# Description: https://python-mip.readthedocs.io/en/latest/examples.html#resource-constrained-project-scheduling

# Data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]]
resource_capacities_data = [6, 8]
successors_link_data = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]]
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json

# Parameters
durations = np.array(durations_data)
resource_needs = np.array(resource_needs_data)
resource_capacities = np.array(resource_capacities_data)
successors_link = np.array(successors_link_data)

nb_resource = len(resource_capacities)
nb_jobs = len(durations)
max_duration = sum(durations)  # dummy upper bound, can be improved of course

# Decision Variables
start_time = intvar(0, max_duration, shape=nb_jobs)  # start time of each job

model = Model()

# Precedence constraints
for j in range(successors_link.shape[0]):
    model += start_time[successors_link[j, 1]] >= start_time[successors_link[j, 0]]+durations[successors_link[j, 0]]

# Cumulative resource constraint
for r in range(nb_resource):
    model += Cumulative(start=start_time, duration=durations, end=start_time+durations, demand=resource_needs[:, r], capacity=resource_capacities[r])

makespan = max(start_time)
model.minimize(makespan)

# Solve
model.solve()

# Print
solution = {"start_time": start_time.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
