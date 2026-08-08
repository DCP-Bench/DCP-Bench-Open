
import cpmpy as cp
import json

# Input data
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
open_warehouses = cp.boolvar(shape=4, name="open_warehouses")
ships = cp.intvar(0, max_shipping, shape=(4, 3), name="ships")

# Constraints

# 1. Demand constraints for each region
for region in range(3):
    model += cp.sum(ships[:, region]) >= demands[region]

# 2. Max shipping per warehouse (sum across regions <= max if open)
for warehouse in range(4):
    model += cp.sum(ships[warehouse, :]) <= max_shipping * open_warehouses[warehouse]

# 3. If New York is open, Los Angeles must also be open
model += open_warehouses[0].implies(open_warehouses[1])

# 4. No more than three warehouses can be open
model += cp.sum(open_warehouses) <= 3

# 5. Either Atlanta or Los Angeles must be open
model += (open_warehouses[1] | open_warehouses[3])

# Objective: minimize total cost (fixed + shipping)
fixed_cost = cp.sum(open_warehouses * fixed_costs)
shipping_cost = cp.sum(ships[i, j] * shipping_costs[i][j] for i in range(4) for j in range(3))
total_cost = fixed_cost + shipping_cost
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {
        'total_cost': int(model.objective_value()),
        'open_warehouse': [int(v) for v in open_warehouses.value()],
        'ships': ships.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
