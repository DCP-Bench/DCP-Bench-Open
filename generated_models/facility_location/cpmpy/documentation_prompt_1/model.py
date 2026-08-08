
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
num_warehouses = len(warehouse_s)
num_regions = len(demands)

# Model definition
model = cp.Model()

# Decision Variables
# open_warehouse[i] = 1 if warehouse i is open, else 0
open_warehouse = cp.boolvar(shape=num_warehouses, name="open_warehouse")

# ships[i,j] = units shipped from warehouse i to region j
# domain: 0 to max_shipping (max units per warehouse)
ships = cp.intvar(0, max_shipping, shape=(num_warehouses, num_regions), name="ships")

# Constraints

# 1. If New York warehouse is opened, then Los Angeles warehouse must also be opened.
# New York index = 0, Los Angeles index = 1
model += open_warehouse[0] <= open_warehouse[1]

# 2. No more than three warehouses can be operational in any given week.
model += cp.sum(open_warehouse) <= 3

# 3. Either the Atlanta or the Los Angeles warehouse must be opened.
# Atlanta index = 3, Los Angeles index = 1
model += (open_warehouse[3] + open_warehouse[1]) >= 1

# 4. Demand satisfaction: sum of shipments to each region must be at least the demand
for j in range(num_regions):
    model += cp.sum(ships[:, j]) >= demands[j]

# 5. Shipments from a warehouse cannot exceed max_shipping if warehouse is open, else zero
for i in range(num_warehouses):
    # sum of shipments from warehouse i <= max_shipping * open_warehouse[i]
    model += cp.sum(ships[i, :]) <= max_shipping * open_warehouse[i]

# Objective: minimize total cost = sum of fixed costs for open warehouses + sum of shipping costs
fixed_cost_total = cp.sum([fixed_costs[i] * open_warehouse[i] for i in range(num_warehouses)])
shipping_cost_total = cp.sum([ships[i, j] * shipping_costs[i][j] for i in range(num_warehouses) for j in range(num_regions)])
total_cost = fixed_cost_total + shipping_cost_total

model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {
        'total_cost': int(model.objective_value()),
        'open_warehouse': open_warehouse.value().astype(int).tolist(),
        'ships': ships.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
