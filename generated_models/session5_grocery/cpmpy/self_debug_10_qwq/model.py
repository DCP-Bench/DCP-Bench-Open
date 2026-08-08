
import cpmpy as cp
import json

model = cp.Model()

# Define variables for the four prices in cents, each between 1 and 711
prices = cp.intvar(1, 711, shape=4, name="prices")

# Constraints
# Sum of prices must be 711 cents
model += (cp.sum(prices) == 711)
# Product of prices must be 711000000 (corrected to use explicit multiplication)
model += (prices[0] * prices[1] * prices[2] * prices[3] == 711000000)
# Order the variables to reduce symmetry (a <= b <= c <= d)
model += [prices[0] <= prices[1], prices[1] <= prices[2], prices[2] <= prices[3]]

# Solve the model
if model.solve():
    solution = {'prices': prices.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
