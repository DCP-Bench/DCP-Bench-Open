
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

# Model definition
model = cp_model.CpModel()

# Decision Variables
# open_warehouse[i] = 1 if warehouse i is open, 0 otherwise
open_warehouse = [model.NewBoolVar(f"open_warehouse[{i}]") for i in range(len(warehouse_s))]

# ships[i][j] = units shipped from warehouse i to region j
ships = []
for i in range(len(warehouse_s)):
    row = []
    for j in range(len(demands)):
        # Upper bound on shipping is the demand of region j
        row.append(model.NewIntVar(0, demands[j], f"ships[{i}][{j}]"))
    ships.append(row)

# Constraints

# 1. If New York is opened (index 0), then Los Angeles (index 1) must be opened
model.Add(open_warehouse[0] <= open_warehouse[1])

# 2. No more than three warehouses can be operational in any given week
model.Add(sum(open_warehouse) <= 3)

# 3. Either Atlanta (index 3) or Los Angeles (index 1) must be opened
model.Add(open_warehouse[3] + open_warehouse[1] >= 1)

# 4. Shipping capacity constraint per warehouse
for i in range(len(warehouse_s)):
    model.Add(sum(ships[i][j] for j in range(len(demands))) <= max_shipping * open_warehouse[i])

# 5. Demand satisfaction: each region's total shipments must meet demand
for j in range(len(demands)):
    model.Add(sum(ships[i][j] for i in range(len(warehouse_s))) == demands[j])

# Objective function: minimize fixed costs + shipping costs
fixed_cost_term = sum(fixed_costs[i] * open_warehouse[i] for i in range(len(warehouse_s)))
shipping_cost_term = sum(shipping_costs[i][j] * ships[i][j] 
                         for i in range(len(warehouse_s)) 
                         for j in range(len(demands)))
model.Minimize(fixed_cost_term + shipping_cost_term)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'total_cost': solver.ObjectiveValue(),
        'open_warehouse': [solver.Value(open_warehouse[i]) for i in range(len(warehouse_s))],
        'ships': [
            [solver.Value(ships[i][j]) for j in range(len(demands))]
            for i in range(len(warehouse_s))
        ]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
