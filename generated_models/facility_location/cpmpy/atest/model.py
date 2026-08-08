from cpmpy import *
import json

# Input data
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

# Number of warehouses and regions
num_warehouses = len(warehouse_s)
num_regions = len(demands)

# Decision variables
open_warehouse = boolvar(shape=num_warehouses, name="open_warehouse")
ships = intvar(0, max_shipping, shape=(num_warehouses, num_regions), name="ships")

# Model
model = Model()

# Objective: minimize total cost (fixed + shipping)
total_fixed_cost = sum(open_warehouse * fixed_costs)
total_shipping_cost = sum(ships * shipping_costs)
model.minimize(total_fixed_cost + total_shipping_cost)

# Constraints
# 1. If New York is opened, then Los Angeles must also be opened
model += [open_warehouse[0] <= open_warehouse[1]]

# 2. No more than three warehouses can be opened
model += [sum(open_warehouse) <= 3]

# 3. Either Atlanta or Los Angeles must be opened
model += [open_warehouse[1] + open_warehouse[3] >= 1]

# 4. Shipments from a warehouse can only occur if it is open
for w in range(num_warehouses):
    for r in range(num_regions):
        model += [ships[w, r] <= open_warehouse[w] * max_shipping]

# 5. Total shipments to each region must meet the demand
for r in range(num_regions):
    model += [sum(ships[:, r]) == demands[r]]

# Solve the model
model.solve()

# Compute total cost
total_fixed_cost_val = sum(open_warehouse.value() * fixed_costs)
total_shipping_cost_val = sum(ships.value() * shipping_costs)
total_cost_val = total_fixed_cost_val + total_shipping_cost_val

# Prepare solution
solution = {
    "total_cost": total_cost_val,
    "open_warehouse": [int(open_warehouse[i].value()) for i in range(num_warehouses)],
    "ships": ships.value().tolist()
}
print(json.dumps(solution))