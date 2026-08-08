
import cpmpy as cp
import numpy as np
import json

# Data
input_data = {
    "supply": [8, 7],
    "demand": [5, 10],
    "cost": [[10, 20], [15, 25]],
    "limit": [[5, 6], [4, 6]]
}
supply = input_data["supply"]
demand = input_data["demand"]
cost = input_data["cost"]
limit = input_data["limit"]

supply_np = np.array(supply)
demand_np = np.array(demand)
cost_np = np.array(cost)
limit_np = np.array(limit)

n_people = len(supply_np)
n_projects = len(demand_np)

# Model definition
model = cp.Model()

# Decision Variables
max_limit = int(np.max(limit_np))
assign = cp.intvar(0, max_limit, shape=(n_people, n_projects), name="assign")

# Constraints
# Per-arc limits
model += [assign[i, j] <= int(limit_np[i, j]) for i in range(n_people) for j in range(n_projects)]

# Supply constraints: each person's assigned hours equals their supply
for i in range(n_people):
    model += (cp.sum(assign[i, :]) == int(supply_np[i]))

# Demand constraints: each project's received hours equals its demand
for j in range(n_projects):
    model += (cp.sum(assign[:, j]) == int(demand_np[j]))

# Objective: minimize total cost
total_cost_expr = cp.sum(assign * cost_np)
model.minimize(total_cost_expr)

# Solve and print
if model.solve():
    solution = {
        'assign': assign.value().tolist(),
        'total_cost': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
