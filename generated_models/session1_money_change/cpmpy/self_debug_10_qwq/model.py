
import cpmpy as cp
import json

# Data
coin_values = [1, 2, 5, 10, 25, 50]
available = [20, 10, 15, 8, 4, 2]

# Model definition
model = cp.Model()

# Decision Variables
max_ub = max(available)  # Use the maximum available as a common upper bound
x = cp.intvar(lb=0, ub=max_ub, shape=len(coin_values), name="coin_counts")

# Constraints
# Enforce per-coin availability limits
for i in range(len(coin_values)):
    model += x[i] <= available[i]

# Total value must be 199
total_value = cp.sum(coin_values[i] * x[i] for i in range(len(coin_values)))
model += (total_value == 199)

# Objective: minimize the number of coins
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'coin_counts': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
