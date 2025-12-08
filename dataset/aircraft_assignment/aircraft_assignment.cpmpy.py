#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/aircraft_assignment

"""
This problem involves assigning multiple types of aircraft to a set of routes to minimize the total operational cost.
Each aircraft type has a limited number of available units. Each route has a specific passenger demand that must be satisfied.
For each aircraft type and route, we are given the passenger capacity and the operational cost.
The goal is to determine how many aircraft of each type to assign to each route to meet all passenger demands, stay within the availability limits for each aircraft type, and minimize the overall cost.

Print the allocation matrix (allocation) as a list of lists of integers; allocation[i][j] represents the number of aircraft of type i assigned to route j.
"""

# Data
availability = [2, 3, 1]  # availability[i] is the number of available aircraft of type i
demand = [100, 150]  # demand[j] is the demand for route j
capabilities = [
    [50, 70],  # capabilities[i][j] is the capacity of aircraft type i on route j
    [60, 80],
    [70, 90]
]
costs = [
    [100, 200],  # costs[i][j] is the cost of assigning aircraft type i to route j
    [150, 250],
    [200, 300]
]

# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
capabilities = cpm_array(capabilities)
costs = cpm_array(costs)
num_aircraft = len(availability)
num_routes = len(demand)

# Decision variables
allocation = intvar(0, max(availability), shape=(num_aircraft, num_routes), name="allocation")

# Model
model = Model()

# Objective: Minimize the total cost of the assignment
model.minimize(sum(allocation * costs))

# Constraint 1: The allocation of aircraft `a` does not exceed its availability
for a in range(num_aircraft):
    model += sum(allocation[a, :]) <= availability[a]

# Constraint 2: The total allocation for each route meets the demand
for r in range(num_routes):
    model += sum(allocation[:, r] * capabilities[:, r]) >= demand[r]

# Solve the model
model.solve()

# Print the solution
solution = {"allocation": allocation.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
