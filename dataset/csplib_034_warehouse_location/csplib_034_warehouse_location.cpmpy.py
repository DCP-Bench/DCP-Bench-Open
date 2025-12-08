#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob034/

"""
In the Warehouse Location problem, a company must decide which warehouses to open
from a set of candidate locations to supply a set of stores. Each warehouse has a
fixed maintenance cost and a capacity limiting the number of stores it can supply.
Each store must be supplied by exactly one open warehouse, and there is an
associated supply cost that varies depending on the store and warehouse.

The objective is to minimize the total cost, which is the sum of the maintenance
costs for all opened warehouses and the supply costs for all stores.

Print the minimized total cost (total_cost), a binary list indicating which
warehouses are open (open_warehouses), and an integer list of `n_stores` elements - ranging from 0 to `n_suppliers-1` - showing the warehouse assigned
to each store (supplier_assignment).
"""

# Data
n_suppliers = 5
n_stores = 10
building_cost = 30
capacity = [1, 4, 2, 1, 3]  # capacity of each warehouse
cost_matrix = [  # cost_matrix[store][warehouse]
    [20, 24, 11, 25, 30],
    [28, 27, 82, 83, 74],
    [74, 97, 71, 96, 70],
    [2, 55, 73, 69, 61],
    [46, 96, 59, 83, 4],
    [42, 22, 29, 67, 59],
    [1, 5, 73, 59, 56],
    [10, 73, 13, 43, 96],
    [93, 35, 63, 85, 46],
    [47, 65, 55, 71, 95]
]
# End of data

import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# supplier_assignment[s] = w: which warehouse 'w' supplies store 's'.
supplier_assignment = cp.intvar(0, n_suppliers - 1, shape=n_stores, name="supplier_assignment")
# open_warehouses[w] = 1 if warehouse 'w' is open, 0 otherwise.
open_warehouses = cp.boolvar(shape=n_suppliers, name="open_warehouses")

# Constraints
# 1. The number of stores assigned to a warehouse cannot exceed its capacity.
for w in range(n_suppliers):
    model += (cp.Count(supplier_assignment, w) <= capacity[w])

# 2. Channeling: A warehouse is open if and only if it supplies at least one store.
# This also implicitly ensures that stores are only assigned to open warehouses.
for w in range(n_suppliers):
    model += (open_warehouses[w] == (cp.Count(supplier_assignment, w) > 0))

# Objective
# The objective is to minimize the sum of supply and maintenance costs.
# Convert data matrix to a cpm_array to allow indexing with decision variables.
cost_matrix_cpm = cp.cpm_array(cost_matrix)
supply_cost = cp.sum([cost_matrix_cpm[s, supplier_assignment[s]] for s in range(n_stores)])
maintenance_cost = cp.sum(open_warehouses) * building_cost
total_cost = supply_cost + maintenance_cost

model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {
        "total_cost": int(model.objective_value()),
        "open_warehouses": [int(v) for v in open_warehouses.value()],
        "supplier_assignment": supplier_assignment.value().tolist()
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
# End of CPMpy script