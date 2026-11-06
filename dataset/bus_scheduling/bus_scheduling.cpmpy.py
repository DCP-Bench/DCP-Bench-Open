#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/bus_schedule.py
# Source description: Problem from Taha "Introduction to Operations Research", page 58.

# Data
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
slots = len(demands)

# Decision Variables
# x[i] represents the number of buses scheduled to start working in the i-th 4-hour slot
x = intvar(0, sum(demands), shape=slots, name="x")

# Model the constraints
# Each bus operates for 8 hours, so it covers two consecutive 4-hour slots
constraints = []
for i in range(slots):
    # The number of buses covering the i-th and (i+1)-th slot should meet the demand of the (i+1)-th slot
    constraints.append(x[i] + x[(i + 1) % slots] >= demands[(i + 1) % slots])

# Create the model with constraints
model = Model(constraints)

# Objective: Minimize the total number of buses used
model.minimize(sum(x))

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
