#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/multi

"""
This is a multi-commodity transportation problem. Given a set of origins `Origins`, a set of destinations `Destinations`,
and a set of products `Products`. Each origin `i` has a certain supply of each product `p` `Supply_{i,p}` and each
destination `j` has a certain demand for each product `p` `Demand_{j,p}`. The cost of shipping one unit of product `p`
from origin `i` to destination `j` is `ShippingCost_{i, j, p}`. The problem aims to minimize the total cost of shipping
all products from the origins to the destinations.

Print the optimized cost (total_cost) as an integer.
"""

# Data
supply = [  # supply[i][p] is the supply of product p at origin i
    [20, 30],
    [40, 10]
]
demand = [  # demand[j][p] is the demand of product p at destination j
    [30, 30],
    [30, 10]
]
limit = [  # limit[i][j] is the maximum total amount that can be shipped
    [35, 35],
    [40, 30]
]
cost = [  # cost[i][j][p] is the shipping cost of product p from origin i to destination j
    [
        [2, 3],
        [4, 1]
    ],
    [
        [3, 2],
        [2, 4]
    ]
]
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n_origins = len(supply)
n_destinations = len(demand)
n_products = len(supply[0])
max_supply = max(max(row) for row in supply)
max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

# Decision variables
# Variables: x[i,j,p] is the amount of product p shipped from origin i to destination j
x = intvar(0, max_supply, shape=(n_origins, n_destinations, n_products), name="x")
total_cost = intvar(0, max_total_cost, name="total_cost")

# Model
model = Model()

# Constraint 1: Supply constraints
for i in range(n_origins):
    for p in range(n_products):
        model += sum(x[i, :, p]) <= supply[i][p]

# Constraint 2: Demand constraints
for j in range(n_destinations):
    for p in range(n_products):
        model += sum(x[:, j, p]) >= demand[j][p]

# Constraint 3: Limit constraints
for i in range(n_origins):
    for j in range(n_destinations):
        model += sum(x[i, j, :]) <= limit[i][j]

model += total_cost == sum(x * cost)

# Objective
model.minimize(total_cost)

# Solve the model
model.solve()

# Print the solution
solution = {
    "total_cost": int(total_cost.value())
}
print(json.dumps(solution))
# End of CPMPy script