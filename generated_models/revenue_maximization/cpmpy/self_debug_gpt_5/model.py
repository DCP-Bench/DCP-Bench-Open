
import cpmpy as cp
import json

# Data (optional)
input_data = {
    "available_seats": [50, 60, 70],  # available_seats[j] is the number of available seats on flight leg j
    "demand": [30, 40],  # demand[i] is the estimated demand for package i
    "revenue": [100, 150],  # revenue[i] is the revenue gained from selling package i
    "delta": [[1, 1, 0], [0, 1, 1]]  # delta[i][j] is 1 if package i uses flight leg j, 0 otherwise
}
available_seats = input_data["available_seats"]
demand = input_data["demand"]
revenue = input_data["revenue"]
delta = input_data["delta"]

n_packages = len(demand)
n_legs = len(available_seats)

# Model definition
model = cp.Model()

# Decision Variables
packages_to_sell = cp.intvar(0, max(demand), shape=n_packages, name="packages_to_sell")

# Constraints
# - Demand constraints
for i in range(n_packages):
    model += (packages_to_sell[i] <= demand[i])

# - Capacity constraints per flight leg
for j in range(n_legs):
    model += (cp.sum([packages_to_sell[i] * delta[i][j] for i in range(n_packages)]) <= available_seats[j])

# Objective (maximize revenue)
model.maximize(cp.sum([revenue[i] * packages_to_sell[i] for i in range(n_packages)]))

# Solve and print
if model.solve():
    solution = {
        'packages_to_sell': packages_to_sell.value().tolist(),
        'max_revenue': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
