#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/prod

# Data
a = [3, 1, 2]
c = [5, 10, 8]
u = [4, 6, 3]
b = 4
# End of data

# Import libraries
from cpmpy import *
import json
import math

# Data unpacking
num_products = len(a)


# Decision variables
x = intvar(0, max(u), shape=num_products, name="x")  # Production quantities for each product

# Model
model = Model()

# Objective: Maximize the total profit
total_profit = sum(c[j] * x[j] for j in range(num_products))
model.maximize(total_profit)

# Constraint: The sum of (1/a[j]) * X[j] should be less than or equal to b
# Or, to remove divisions, we multiply both sides with the least common multiple of a
lcm_a = math.lcm(*a)  # Least common multiple of all a[j]
model += sum((lcm_a // a[j]) * x[j] for j in range(num_products)) <= b * lcm_a

# Constraint: X[j] should be between 0 and u[j] for all j in P
for j in range(num_products):
    model += (0 <= x[j]) & (x[j] <= u[j])

# Solve the model
model.solve()

# Print the solution
solution = {
    "x": x.value().tolist(),
    "total_profit": int(model.objective_value())
}
print(json.dumps(solution))
# End of CPMPy script