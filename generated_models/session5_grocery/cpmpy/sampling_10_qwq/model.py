
import cpmpy as cp
import json

model = cp.Model()

# Decision variables: four integers between 1 and 711 (prices in cents)
prices = cp.intvar(1, 711, shape=4)

# Constraints
model += [cp.sum(prices) == 711,  # Sum to 711 cents
          prices[0] * prices[1] * prices[2] * prices[3] == 711000000,  # Product equals 711000000
          cp.Increasing(prices)]  # Order variables to reduce symmetry

# Solve and print
if model.solve():
    solution = {'prices': prices.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
