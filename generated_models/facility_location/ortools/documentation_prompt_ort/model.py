from ortools.sat.python import cp_model
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
    [24, 50, 35]   # Atlanta to regions 1, 2, 3
]

num_warehouses = len(warehouse_s)
num_regions = len(demands)

# Model definition
model = cp_model.CpModel()

# Decision Variables
# open_warehouse[i] = 1 if warehouse i is open, 0 otherwise
open_warehouse = [model.NewBoolVar(f'open_{warehouse_s[i]}') for i in range(num_warehouses)]

# ships[i][j] = units shipped from warehouse i to region j
# Since max shipping per warehouse is 100, upper bound is max_shipping
ships = []
for i in range(num_warehouses):
    row = []
    for j in range(num_regions):
        # Shipments are integers >= 0 and <= max_shipping (warehouse capacity)
        var = model.NewIntVar(0, max_shipping, f'ship_{warehouse_s[i]}_to_region{j+1}')
        row.append(var)
    ships.append(row)

# Constraints

# 1. If New York warehouse is opened, then Los Angeles warehouse must also be opened.
# New York index = 0, Los Angeles index = 1
model.AddImplication(open_warehouse[0], open_warehouse[1])

# 2. No more than three warehouses can be operational in any given week.
model.Add(sum(open_warehouse) <= 3)

# 3. Either the Atlanta or the Los Angeles warehouse must be opened.
# Atlanta index = 3, Los Angeles index = 1
model.AddBoolOr([open_warehouse[3], open_warehouse[1]])

# 4. Shipments from a warehouse can only happen if the warehouse is open.
for i in range(num_warehouses):
    for j in range(num_regions):
        # ships[i][j] <= max_shipping * open_warehouse[i]
        # If warehouse is closed (0), ships[i][j] must be 0
        model.Add(ships[i][j] <= max_shipping * open_warehouse[i])

# 5. Total shipments from each warehouse cannot exceed max_shipping
for i in range(num_warehouses):
    model.Add(sum(ships[i][j] for j in range(num_regions)) <= max_shipping)

# 6. Demand for each region must be met exactly
for j in range(num_regions):
    model.Add(sum(ships[i][j] for i in range(num_warehouses)) == demands[j])

# Objective: Minimize total cost = sum of fixed costs for open warehouses + sum of shipping costs
fixed_cost_term = sum(fixed_costs[i] * open_warehouse[i] for i in range(num_warehouses))
shipping_cost_term = sum(shipping_costs[i][j] * ships[i][j] for i in range(num_warehouses) for j in range(num_regions))
model.Minimize(fixed_cost_term + shipping_cost_term)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'total_cost': solver.ObjectiveValue(),
        'open_warehouse': [solver.Value(var) for var in open_warehouse],
        'ships': [[solver.Value(ships[i][j]) for j in range(num_regions)] for i in range(num_warehouses)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")