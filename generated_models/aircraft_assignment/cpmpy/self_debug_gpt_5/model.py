
import cpmpy as cp
import json

# Data
input_data = {
    "availability": [2, 3, 1],  # availability[i] is the number of available aircraft of type i
    "demand": [100, 150],  # demand[j] is the demand for route j
    "capabilities": [
        [50, 70],  # capabilities[i][j] is the capacity of aircraft type i on route j
        [60, 80],
        [70, 90]
    ],
    "costs": [
        [100, 200],  # costs[i][j] is the cost of assigning aircraft type i to route j
        [150, 250],
        [200, 300]
    ]
}
# End of data

availability = input_data["availability"]
demand = input_data["demand"]
capabilities = input_data["capabilities"]
costs = input_data["costs"]

n_types = len(availability)
n_routes = len(demand)

# Model definition
model = cp.Model()

# Decision Variables
max_avail = max(availability) if availability else 0
allocation = cp.intvar(0, max_avail, shape=(n_types, n_routes), name="allocation")

# Constraints

# 1) Availability constraints: sum of assigned aircraft per type does not exceed availability
for i in range(n_types):
    model += (cp.sum([allocation[i, j] for j in range(n_routes)]) <= availability[i])

# 2) Demand constraints: capacity provided on each route meets or exceeds demand
for j in range(n_routes):
    model += (cp.sum([allocation[i, j] * capabilities[i][j] for i in range(n_types)]) >= demand[j])

# Objective: Minimize total operational cost
total_cost = cp.sum([allocation[i, j] * costs[i][j] for i in range(n_types) for j in range(n_routes)])
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {'allocation': allocation.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
