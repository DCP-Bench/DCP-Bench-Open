
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: prices in cents (positive integers)
prices = cp.intvar(1, 711, shape=4, name="prices")  # each price between 1 and 711 cents

# Constraints
model += cp.sum(prices) == 711  # sum to $7.11 -> 711 cents
# product of prices in dollars equals $7.11:
# (p1/100)*(p2/100)*(p3/100)*(p4/100) = 711/100
# => p1*p2*p3*p4 = 711 * 100^3 = 711000000
model += prices[0] * prices[1] * prices[2] * prices[3] == 711000000

# Break symmetry to get a canonical solution ordering
model += cp.Increasing(prices)

# Solve and print
if model.solve():
    solution = {'prices': prices.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
