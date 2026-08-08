
import cpmpy as cp
import json

# Data
warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"]
fixed_costs = [400, 500, 300, 150]  # Weekly fixed costs per warehouse
max_shipping = 100  # Max units per week per warehouse (total capacity)
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
m = len(warehouse_s)   # number of warehouses (4)
n = len(demands)       # number of regions (3)

open_warehouse = cp.boolvar(shape=m, name="open_warehouse")         # 1 if warehouse i is opened
ships = cp.intvar(0, max_shipping, shape=(m, n), name="ships")     # shipments from warehouse i to region j

# Constraints
# 1) If New York (index 0) is opened, then Los Angeles (index 1) must be opened
model += open_warehouse[0].implies(open_warehouse[1])

# 2) No more than three warehouses can be operational in any given week
model += cp.sum(open_warehouse) <= 3

# 3) Either Atlanta (index 3) or Los Angeles (index 1) must be opened
model += (open_warehouse[3] + open_warehouse[1] >= 1)

# 4) Demands for each region must be satisfied exactly
for j in range(n):
    model += cp.sum([ships[i, j] for i in range(m)]) == demands[j]

# 5) Warehouse capacity: total shipped from a warehouse cannot exceed max_shipping if opened, else 0
for i in range(m):
    model += cp.sum([ships[i, j] for j in range(n)]) <= max_shipping * open_warehouse[i]

# 6) If a warehouse is closed, its shipments must be zero (ensured by previous constraint and non-negativity)
#    Additionally, each individual route cannot exceed max_shipping (already enforced by variable bounds)

# Objective: minimize fixed opening costs plus shipping costs
fixed_cost_term = cp.sum([fixed_costs[i] * open_warehouse[i] for i in range(m)])
shipping_cost_term = cp.sum([shipping_costs[i][j] * ships[i, j] for i in range(m) for j in range(n)])
total_cost_expr = fixed_cost_term + shipping_cost_term

model.minimize(total_cost_expr)

# Solve and print
if model.solve():
    # Convert boolean list to 0/1 integers as requested
    open_vals_bool = open_warehouse.value().tolist()
    open_vals = [int(x) for x in open_vals_bool]
    ships_vals = ships.value().tolist()
    solution = {
        'total_cost': int(model.objective_value()),
        'open_warehouse': open_vals,
        'ships': ships_vals
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
