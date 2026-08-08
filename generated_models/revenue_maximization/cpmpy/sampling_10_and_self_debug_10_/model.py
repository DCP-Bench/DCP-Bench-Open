
import cpmpy as cp
import json

# Data
input_data = {
    "available_seats": [50, 60, 70],  # available_seats[j] is the number of available seats on flight leg j
    "demand": [30, 40],  # demand[i] is the estimated demand for package i
    "revenue": [100, 150],  # revenue[i] is the revenue gained from selling package i
    "delta": [[1, 1, 0], [0, 1, 1]]  # delta[i][j] is 1 if package i uses flight leg j, 0 otherwise
}
# End of data

# Model definition
model = cp.Model()

# Extract data
available_seats = input_data["available_seats"]
demand = input_data["demand"]
revenue = input_data["revenue"]
delta = input_data["delta"]

num_packages = len(demand)
num_legs = len(available_seats)

# Decision Variables
packages_to_sell = cp.intvar(0, max(demand), shape=num_packages, name="packages_to_sell")

# Constraints
# Each package sold cannot exceed its demand
for i in range(num_packages):
    model += (packages_to_sell[i] <= demand[i])

# Seat capacity constraints for each flight leg
for j in range(num_legs):
    model += (cp.sum([delta[i][j] * packages_to_sell[i] for i in range(num_packages)]) <= available_seats[j])

# Objective: maximize total revenue
total_revenue = cp.sum([revenue[i] * packages_to_sell[i] for i in range(num_packages)])
model.maximize(total_revenue)

# Solve and print
if model.solve():
    solution = {
        'packages_to_sell': packages_to_sell.value().tolist(),
        'max_revenue': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
