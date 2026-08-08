
import cpmpy as cp
import json

# Data
coin_types = [16, 17, 23, 24, 39, 40]
total_coins_stolen = 100

# Model definition
model = cp.Model()

# Decision Variables: number of bags stolen for each coin type
bags = cp.intvar(0, total_coins_stolen, shape=len(coin_types), name="bags")

# Constraints
# Total coins stolen must be exactly 100
model += (cp.sum([bags[i] * coin_types[i] for i in range(len(coin_types))]) == total_coins_stolen)

# Solve and print
if model.solve():
    solution = {'bags': bags.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
