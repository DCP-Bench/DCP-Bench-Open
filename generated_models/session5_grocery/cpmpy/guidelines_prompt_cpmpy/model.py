
import cpmpy as cp
import json

# No external data

# Model definition
model = cp.Model()

# Decision Variables: prices in cents, positive integers
prices = cp.intvar(1, 711, shape=4, name="prices")

# Constraints
# Sum of prices is 711 cents ($7.11)
model += cp.sum(prices) == 711

# Product of prices is 711,000,000 (since (p/100)^4 product = 7.11 -> p1*p2*p3*p4 = 7.11*100^4 = 711,000,000)
model += prices[0] * prices[1] * prices[2] * prices[3] == 711000000

# Solve and print
if model.solve():
    solution = {'prices': prices.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
