
import cpmpy as cp
import json

# Data
scores = [16, 17, 23, 24, 39, 40]
target = 100
n = len(scores)

# Decision variable upper bound (enough to cover all possibilities near target)
ub = target // min(scores) + 10  # e.g., 16 + 10 = 26

# Model definition
model = cp.Model()

# Decision Variables
hits = cp.intvar(0, ub, shape=n, name="hits")

# Constraints and Objective
total = cp.sum([scores[i] * hits[i] for i in range(n)])

# Objective: minimize the absolute difference to target
model.minimize(cp.Abs(total - target))

# Solve and print
if model.solve():
    solution = {'hits': hits.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
