#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/revenue_maximization

# Data
available_seats = [50, 60, 70]  # available_seats[j] is the number of available seats on flight leg j
demand = [30, 40]  # demand[i] is the estimated demand for package i
revenue = [100, 150]  # revenue[i] is the revenue gained from selling package i
delta = [[1, 1, 0], [0, 1, 1]]  # delta[i][j] is 1 if package i uses flight leg j, 0 otherwise
# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
delta = cpm_array(delta)

num_packages = len(demand)
num_legs = len(available_seats)

# Decision variables
packages_to_sell = intvar(0, max(demand), shape=num_packages, name="packages_to_sell")

# Model
model = Model()

# Capacity constraints for each flight leg
for j in range(num_legs):
    model += sum([delta[i, j] * packages_to_sell[i] for i in range(num_packages)]) <= available_seats[j]

# Demand constraints for each package
for i in range(num_packages):
    model += packages_to_sell[i] <= demand[i]

# Objective: Maximize revenue
max_revenue = sum(revenue * packages_to_sell)
model.maximize(max_revenue)

# Solve the model
model.solve()

# Print the solution
solution = {
    "packages_to_sell": packages_to_sell.value().tolist(),
    "max_revenue": int(model.objective_value())
}
print(json.dumps(solution))

# End of CPMPy script