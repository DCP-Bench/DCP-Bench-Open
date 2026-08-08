
import cpmpy as cp
import json

targets = [16, 17, 23, 24, 39, 40]

# Model definition
model = cp.Model()

# Decision Variables
hits = cp.intvar(0, 1000, shape=len(targets), name="hits")

# Total score calculation
total = cp.sum(targets[i] * hits[i] for i in range(6))

# Compute the absolute difference from 100
difference = cp.Abs(total - 100)

# Objective: minimize difference (prioritized) and maximize the number of arrows
sum_hits = cp.sum(hits)
objective = difference * 1000000 - sum_hits  # Prioritize difference first
model.minimize(objective)

# Solve and print
if model.solve():
    solution = {'hits': hits.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
