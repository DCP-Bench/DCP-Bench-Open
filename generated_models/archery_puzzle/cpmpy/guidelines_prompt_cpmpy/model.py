
import cpmpy as cp
import json

# Data
targets = [16, 17, 23, 24, 39, 40]
n_targets = len(targets)
# Upper bound on arrows: enough to exceed 100 by a bit
max_arrows = (100 // min(targets)) + 1
# End of data

# Model definition
model = cp.Model()

# Decision Variables
hits = cp.intvar(0, max_arrows, shape=n_targets, name="hits")
# Total score
score = cp.sum([hits[i] * targets[i] for i in range(n_targets)])
# Absolute deviation from 100
d = cp.intvar(0, max_arrows * max(targets), name="d")

# Constraints
model += d >= score - 100
model += d >= 100 - score

# Objective: minimize the distance to 100
model.minimize(d)

# Solve and print
if model.solve():
    solution = {'hits': hits.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
