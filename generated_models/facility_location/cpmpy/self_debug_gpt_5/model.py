
import cpmpy as cp
import numpy as np
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

# Convert lists to numpy arrays for vectorized operations
fixed_costs = np.array(fixed_costs)
demands = np.array(demands)
shipping_costs = np.array(shipping_costs)

n_w = len(warehouse_s)
n_r = len(demands)

# Model definition
model = cp.Model()

# Decision Variables
open_warehouse = cp.boolvar(shape=n_w, name="open_warehouse")
ships = cp.intvar(0, max_shipping, shape=(n_w, n_r), name="ships")

# Constraints

# 1. If New York is opened, then Los Angeles must also be opened
model += open_warehouse[0].implies(open_warehouse[1])

# 2. No more than three warehouses can be operational
model += (cp.sum(open_warehouse) <= 3)

# 3. Either Atlanta or Los Angeles must be opened
model += (cp.sum([open_warehouse[1], open_warehouse[3]]) >= 1)

# 4. Capacity linking: shipments only if warehouse is open, and respect max capacity per warehouse
for i in range(n_w):
    model += (cp.sum(ships[i, :]) <= max_shipping * open_warehouse[i])

# 5. Meet regional demands exactly
for j in range(n_r):
    model += (cp.sum(ships[:, j]) == demands[j])

# Objective: Minimize total cost = fixed opening costs + shipping costs
total_fixed_cost = cp.sum(fixed_costs * open_warehouse)
total_shipping_cost = cp.sum(shipping_costs * ships)
total_cost_expr = total_fixed_cost + total_shipping_cost

model.minimize(total_cost_expr)

# Solve and print
if model.solve():
    open_vals = [int(v) for v in open_warehouse.value().tolist()]
    solution = {
        'total_cost': int(model.objective_value()),
        'open_warehouse': open_vals,
        'ships': ships.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
