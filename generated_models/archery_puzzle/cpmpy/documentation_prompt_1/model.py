
import cpmpy as cp
import json

# Data
targets = [16, 17, 23, 24, 39, 40]
n_targets = len(targets)
max_arrows = 100  # upper bound on number of arrows (arbitrary large enough)

# Model definition
model = cp.Model()

# Decision Variables: number of hits on each target (non-negative integers)
hits = cp.intvar(0, max_arrows, shape=n_targets, name="hits")

# Total score
total_score = cp.sum([hits[i] * targets[i] for i in range(n_targets)])

# We want to get as close as possible to 100 (either <= or >=)
# So minimize the absolute difference |total_score - 100|
diff = cp.intvar(0, 1000, name="diff")  # large enough upper bound for difference

model += (diff == cp.Abs(total_score - 100))

# Objective: minimize the difference
model.minimize(diff)

# Solve and print
if model.solve():
    solution = {'hits': hits.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
