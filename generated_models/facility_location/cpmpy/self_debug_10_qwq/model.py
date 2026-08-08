
import cpmpy as cp
import json
import numpy as np

# Data
warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"]
fixed_costs = [400, 500, 300, 150]
max_shipping = 100
demands = [80, 70, 40]
shipping_costs = [
    [20, 40, 50],  # New York
    [48, 15, 26],  # Los Angeles
    [26, 35, 18],  # Chicago
    [24, 50, 35]   # Atlanta
]

# Model definition
model = cp.Model()

# Decision variables
open = cp.boolvar(shape=4, name="open")
ships = cp.intvar(0, max_shipping, shape=(4, 3), name="ships")

# Constraints
# 1. If New York is open, then Los Angeles must be open
model += open[0] <= open[1]

# 2. No more than three warehouses open
model += cp.sum(open) <= 3

# 3. Either Atlanta or Los Angeles must be open
model += open[1] + open[3] >= 1

# Demand constraints for each region
for r in range(3):
    model += cp.sum(ships[:, r]) == demands[r]

# Shipping capacity per warehouse
for w in range(4):
    model += cp.sum(ships[w, :]) <= max_shipping * open[w]

# Objective: minimize total cost
fixed_cost = cp.sum(open * fixed_costs)
shipping_cost = cp.sum(ships * np.array(shipping_costs))
model.minimize(fixed_cost + shipping_cost)

# Solve and print
if model.solve():
    # Convert open_warehouse to integers (0/1) instead of booleans
    open_warehouse = [int(v) for v in open.value().tolist()]
    solution = {
        'total_cost': int(model.objective_value()),
        'open_warehouse': open_warehouse,
        'ships': ships.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
