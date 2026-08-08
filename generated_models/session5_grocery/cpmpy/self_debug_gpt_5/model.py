
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
prices = cp.intvar(1, 711, shape=4, name="prices")

# Constraints
model += cp.Increasing(prices)               # symmetry breaking
model += (cp.sum(prices) == 711)             # sum in cents
model += (prices[0] * prices[1] * prices[2] * prices[3] == 711000000)  # product matches $7.11 in cents scaling

# Solve and print
if model.solve():
    solution = {'prices': prices.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
