
import cpmpy as cp
import json
import numpy as np

# Data
coin_values = np.array([1, 2, 5, 10, 25, 50])
available = np.array([20, 10, 15, 8, 4, 2])

model = cp.Model()

# Variables
max_ub = available.max()
coin_counts = cp.intvar(lb=0, ub=max_ub, shape=len(coin_values), name="coins")

# Constraints
# Each coin count cannot exceed available quantities
for i in range(len(available)):
    model += coin_counts[i] <= available[i]

# Total value must be 199 euros
model += cp.sum(coin_counts * coin_values) == 199

# Objective: minimize the number of coins
model.minimize(cp.sum(coin_counts))

# Solve and print
if model.solve():
    solution = {'coin_counts': coin_counts.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
