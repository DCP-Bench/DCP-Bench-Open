#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/facility_location_problem.py

"""
A company is considering opening warehouses in four cities to meet regional demands at minimal costs. The potential
cities for these warehouses are New York, Los Angeles, Chicago, and Atlanta. The company needs to decide which 
warehouses to open based on several constraints: 1. If the New York warehouse is opened, then the Los Angeles 
warehouse must also be opened. 2. No more than three warehouses can be operational in any given week. 3. Either the 
Atlanta or the Los Angeles warehouse must be opened. The objective is to determine the optimal set of warehouses to open
and the distribution of shipments to various regions to minimize total costs.

Print the total cost (total_cost) as an integer, whether the warehouses are open (open_warehouse) as a list of booleans, and the shipping details for each
region per warehouse (ships) as a list of lists where ships[i][j] indicates the number of units shipped from warehouse i to region j - including the non-opened warehouses as 0s.
"""

# Data
warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"]
fixed_costs = [400, 500, 300, 150]  # Weekly fixed costs per warehouse
max_shipping = 100  # Max units per week per warehouse
demands = [80, 70, 40]  # Weekly demands for regions 1 to 3
shipping_costs = [
    [20, 40, 50],  # New York to regions 1, 2, 3
    [48, 15, 26],  # Los Angeles to regions 1, 2, 3
    [26, 35, 18],  # Chicago to regions 1, 2, 3
    [24, 50, 35]  # Atlanta to regions 1, 2, 3
]
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
num_companies = len(warehouse_s)
num_regions = len(demands)
new_york, los_angeles, chicago, atlanta = range(num_companies)
costs = cpm_array(shipping_costs)

# Decision Variables
open_warehouse = boolvar(shape=num_companies, name="open_warehouse")  # 1 if the warehouse is open, 0 otherwise
ships = intvar(0, max_shipping, shape=(num_companies, num_regions), name="ships")  # what to ship to each region
total_cost = intvar(0, 10000, name="total_cost")  # total cost of shipping

# Model
model = Model()

# each warehouse can only send max 100 units per week
for i in range(num_companies):
    model += sum(ships[i, :]) <= max_shipping * open_warehouse[i]

# the demands of the regions
for j in range(num_regions):
    model += sum([ships[i, j] for i in range(num_regions)]) >= demands[j]

# total cost
model += [total_cost == sum(
    [open_warehouse[i] * fixed_costs[i] + sum([ships[i, j] * costs[i, j] for j in range(num_regions)]) for i in
     range(num_companies)])]

# 1. If the New York warehouse is opened, then the Los Angeles warehouse must be opened.
model += open_warehouse[new_york].implies(open_warehouse[los_angeles])

# 2. At most three warehouses can be opened.
model += sum(open_warehouse) <= 3

# 3. Either the Atlanta or the Los Angeles warehouse must be opened.
model += open_warehouse[atlanta] | open_warehouse[los_angeles]

# Objective: Minimize total cost
model.minimize(total_cost)

# Solve
model.solve()

# Print
solution = {"total_cost": total_cost.value(),
            "open_warehouse": open_warehouse.value().tolist(),
            "ships": ships.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
