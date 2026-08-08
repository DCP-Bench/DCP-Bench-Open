
import cpmpy as cp
import numpy as np
import json

# Data
denoms = np.array([1, 2, 5, 10, 25, 50], dtype=int)
avail = np.array([20, 10, 15, 8, 4, 2], dtype=int)
target = 199
# End of data

# Model definition
model = cp.Model()

# Decision Variables
coin_counts = cp.intvar(0, int(avail.max()), shape=6, name="coin_counts")

# Constraints
model += (coin_counts <= avail)
model += (cp.sum(coin_counts * denoms) == target)

# Objective
model.minimize(cp.sum(coin_counts))

# Solve and print
if model.solve():
    solution = {'coin_counts': coin_counts.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
