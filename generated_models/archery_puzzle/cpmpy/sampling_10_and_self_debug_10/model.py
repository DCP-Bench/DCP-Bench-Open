
import cpmpy as cp
import json

# Data
targets = [16, 17, 23, 24, 39, 40]
n_targets = len(targets)

# Model definition
model = cp.Model()

# Decision Variables: number of hits on each target (non-negative integers)
hits = cp.intvar(0, 100, shape=n_targets, name="hits")

# Total score
total_score = cp.sum([hits[i] * targets[i] for i in range(n_targets)])

# We want to get as close as possible to 100 (either below or above)
# Introduce a variable for the absolute difference from 100
diff = cp.intvar(0, 1000, name="diff")

# Constraints for diff = |total_score - 100|
model += (diff >= total_score - 100)
model += (diff >= 100 - total_score)

# Objective: minimize the difference
model.minimize(diff)

# Solve and print
if model.solve():
    solution = {'hits': hits.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
