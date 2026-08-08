
import cpmpy as cp
import json

# Targets
targets = [16, 17, 23, 24, 39, 40]

# Model definition
model = cp.Model()

# Decision Variables: number of hits on each target (0..6 is enough since 7*16 > 100)
hits = cp.intvar(0, 6, shape=6, name="hits")

# Total score variable
total = cp.intvar(0, 100, name="total")

# Constraints
model += (total == cp.sum([targets[i] * hits[i] for i in range(6)]))
model += (total <= 100)

# Objective: get as close as possible to 100
model.maximize(total)

# Solve and print
if model.solve():
    solution = {'hits': hits.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
