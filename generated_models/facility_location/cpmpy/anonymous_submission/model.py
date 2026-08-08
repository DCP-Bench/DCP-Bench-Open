# Import libraries
from cpmpy import *
import json

# Parameters
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

n_warehouses = len(warehouse_s)
n_regions = len(demands)

# Decision Variables
open_warehouse = boolvar(shape=n_warehouses, name="open_warehouse")  # Whether warehouse is open
ships = intvar(0, max_shipping, shape=(n_warehouses, n_regions), name="ships")  # Shipping details
total_cost = intvar(0, sum(fixed_costs) + max_shipping * sum(sum(costs) for costs in shipping_costs), name="total_cost")  # Total cost

# Model
model = Model()

# Constraint 1: If New York is opened, then Los Angeles must also be opened
model += (open_warehouse[0]).implies(open_warehouse[1])

# Constraint 2: No more than three warehouses can be operational
model += sum(open_warehouse) <= 3

# Constraint 3: Either Atlanta or Los Angeles must be opened
model += (open_warehouse[1] | open_warehouse[3])

# Constraint: Demand must be met for each region
for r in range(n_regions):
    model += sum(ships[:, r]) >= demands[r]

# Constraint: Can only ship from open warehouses
for w in range(n_warehouses):
    for r in range(n_regions):
        model += (ships[w, r] > 0).implies(open_warehouse[w])

# Objective: Minimize total cost (fixed + shipping)
model.minimize(
    sum(open_warehouse * fixed_costs) + 
    sum(ships[w, r] * shipping_costs[w][r] for w in range(n_warehouses) for r in range(n_regions))
)

# Link total_cost to the objective expression
model += (total_cost == sum(open_warehouse * fixed_costs) + 
          sum(ships[w, r] * shipping_costs[w][r] for w in range(n_warehouses) for r in range(n_regions)))

# Solve
model.solve()

# Prepare solution with correct key order
solution = {
    "total_cost": int(total_cost.value()),
    "open_warehouse": [bool(val) for val in open_warehouse.value()],
    "ships": ships.value().tolist()
}

print(json.dumps(solution))
# End of CPMPy script