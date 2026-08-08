
import cpmpy as cp
import json

# Data
warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"]
fixed_costs = [400, 500, 300, 150]  # Weekly fixed costs per warehouse
max_shipping = 100  # Max units per week per warehouse
demands = [80, 70, 40]  # Weekly demands for regions 1 to 3
shipping_costs = [
    [20, 40, 50],  # New York to regions 1, 2, 3
    [48, 15, 26],  # Los Angeles to regions 1, 2, 3
    [26, 35, 18],  # Chicago to regions 1, 2, 3
    [24, 50, 35]   # Atlanta to regions 1, 2, 3
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
n_warehouses = len(warehouse_s)
n_regions = len(demands)

# Binary open decision for each warehouse
open_warehouse = cp.boolvar(shape=n_warehouses, name="open_warehouse")

# Shipment quantities from each warehouse to each region
ships = cp.intvar(0, max_shipping, shape=(n_warehouses, n_regions), name="ships")

# Constraints

# 1. If New York (0) is opened, then Los Angeles (1) must be opened.
model += [open_warehouse[0] <= open_warehouse[1]]

# 2. No more than three warehouses can be operational.
model += [cp.sum(open_warehouse) <= 3]

# 3. Either Atlanta (3) or Los Angeles (1) must be opened.
model += [open_warehouse[1] + open_warehouse[3] >= 1]

# 4. Capacity constraints: each warehouse ships at most max_shipping if opened, else 0.
for i in range(n_warehouses):
    model += [cp.sum(ships[i, :]) <= max_shipping * open_warehouse[i]]

# 5. Demand constraints: each region's demand must be met.
for j in range(n_regions):
    model += [cp.sum(ships[:, j]) >= demands[j]]

# Objective: minimize total cost = fixed costs + shipping costs
fixed_cost_term = cp.sum([fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses)])
shipping_cost_term = cp.sum([
    shipping_costs[i][j] * ships[i, j]
    for i in range(n_warehouses) for j in range(n_regions)
])
model.minimize(fixed_cost_term + shipping_cost_term)

# Solve and print
if model.solve():
    open_vals = [int(v) for v in open_warehouse.value().tolist()]
    ships_vals = ships.value().tolist()
    total_cost = int(model.objective_value())
    solution = {
        "total_cost": total_cost,
        "open_warehouse": open_vals,
        "ships": ships_vals
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
