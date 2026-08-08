
import cpmpy as cp
import json

# Data
values = [1, 2, 5, 10, 25, 50]
availability = [20, 10, 15, 8, 4, 2]
target = 199
# End of data

# Model definition
model = cp.Model()

# Decision Variables: number of coins of each type (in the same order as `values`)
max_avail = max(availability)
coin_counts = cp.intvar(0, max_avail, shape=6, name="coin_counts")

# Constraints
# Respect available coins for each type
for i in range(6):
    model += coin_counts[i] <= availability[i]

# Sum of coin values must equal the target amount
model += cp.sum([values[i] * coin_counts[i] for i in range(6)]) == target

# Objective: minimize total number of coins used
model.minimize(cp.sum(coin_counts))

# Solve and print
if model.solve():
    solution = {'coin_counts': coin_counts.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
