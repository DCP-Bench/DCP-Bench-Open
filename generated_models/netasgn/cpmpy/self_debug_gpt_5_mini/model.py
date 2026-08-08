
import cpmpy as cp
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

n_people = len(supply)
n_projects = len(demand)

# Model definition
model = cp.Model()

# Decision Variables: assign[i][j] hours from person i to project j
# Use a uniform upper bound equal to the max limit, and enforce cell-specific limits as constraints
max_limit = max(max(row) for row in limit)
assign = cp.intvar(0, max_limit, shape=(n_people, n_projects), name="assign")

# Constraints
# Each person's assigned hours equals their supply
for i in range(n_people):
    model += (cp.sum([assign[i, j] for j in range(n_projects)]) == supply[i])

# Each project's received hours equals its demand
for j in range(n_projects):
    model += (cp.sum([assign[i, j] for i in range(n_people)]) == demand[j])

# Respect per-person-per-project limits
for i in range(n_people):
    for j in range(n_projects):
        model += (assign[i, j] <= limit[i][j])

# Objective: minimize total cost
objective = cp.sum([assign[i, j] * cost[i][j] for i in range(n_people) for j in range(n_projects)])
model.minimize(objective)

# Solve and print
if model.solve():
    solution = {
        'assign': assign.value().tolist(),
        'total_cost': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
