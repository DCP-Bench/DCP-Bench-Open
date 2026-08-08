
import cpmpy as cp
import json

# Data
values = [1, 2, 5, 10, 25, 50]
availability = [20, 10, 15, 8, 4, 2]
target = 199
# End of data

# Model definition
model = cp.Model()

# Decision Variables
coin_counts = cp.intvar(0, availability, shape=len(values), name="coin_counts")

# Constraints
model += cp.sum([values[i] * coin_counts[i] for i in range(len(values))]) == target

# Objective: minimize the number of coins used
model.minimize(cp.sum(coin_counts))

# Solve and print
if model.solve():
    solution = {
        'coin_counts': coin_counts.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
