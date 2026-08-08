
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

I = len(availability)  # number of aircraft types
J = len(demand)        # number of routes

# Model definition
model = cp.Model()

# Decision Variables
max_avail = max(availability)
allocation = cp.intvar(0, max_avail, shape=(I, J), name="allocation")
# allocation[i, j] = number of aircraft of type i assigned to route j

# Constraints
# 1) For each aircraft type, total assigned across routes <= availability
for i in range(I):
    model += cp.sum(allocation[i, :]) <= availability[i]

# 2) For each route, total capacity provided >= demand
for j in range(J):
    model += cp.sum([capabilities[i][j] * allocation[i, j] for i in range(I)]) >= demand[j]

# Objective: minimize total operational cost
total_cost = cp.sum([costs[i][j] * allocation[i, j] for i in range(I) for j in range(J)])
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {'allocation': allocation.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
