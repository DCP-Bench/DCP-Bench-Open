#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/netasgn

"""
Consider a project assignment problem. Given a set of people `People` and a set of projects `Projects`. Each person `i`
has a certain number of available hours `Supply_{i}` and each project `j` requires a certain number of hours `Demand_{j}`.
The cost per hour of work for person `i` on project `j` is `Cost_{i, j}`. Each person `i` can contribute to project `j`
up to a maximum limit `Limit_{i, j}`. The problem aims to minimize the total cost of assigning people to projects. It is
constrained that the total number of hours assigned from each person `i` equals its supply and the total number of hours
assigned to each project `j` equals its demand. How to decide the number of hours to be assigned from each person `i` to
each project `j`?

Print the hours assigned from each person to each project (assign) as a list of lists of integers, where assign[i][j] is the number of hours assigned from person i to project j,
and the total cost (total_cost).
"""

# Data
supply = [8, 7]
demand = [5, 10]
cost = [[10, 20], [15, 25]]
limit = [[5, 6], [4, 6]]
# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
supply = cpm_array(supply)
demand = cpm_array(demand)
cost = cpm_array(cost)
limit = cpm_array(limit)
num_people = len(supply)
num_projects = len(demand)

# Decision variables
assign = intvar(0, 10, shape=(num_people, num_projects))

# Model
model = Model()

# Constraint 1: The total number of hours assigned from person i equals its supply
for i in range(num_people):
    model += sum(assign[i, :]) == supply[i]

# Constraint 2: The total number of hours assigned to project j equals its demand
for j in range(num_projects):
    model += sum(assign[:, j]) == demand[j]

# Constraint 3: Hours assigned from person i to project j can't exceed the capacity
model += assign <= limit

# Objective: Minimize the total cost of assigning people to projects
total_cost = sum(assign[i, j] * cost[i, j] for i in range(num_people) for j in range(num_projects))
model.minimize(total_cost)

# Solve the model
model.solve()

# Print the solution
solution = {
    "assign": assign.value().tolist(),
    "total_cost": int(model.objective_value())
}
print(json.dumps(solution))

# End of CPMPy script