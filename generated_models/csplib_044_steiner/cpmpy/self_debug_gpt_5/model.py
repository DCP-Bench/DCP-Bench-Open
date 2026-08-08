
import cpmpy as cp
import json

# Data
n = 9  # Order of the Steiner Triple System
# End of data

# Derived parameters
b = n * (n - 1) // 6  # number of triples
r = (n - 1) // 2      # number of triples each element appears in

# Model definition
model = cp.Model()

# Decision Variables
# sets[t, e] = 1 if element e is in triple t, else 0
sets = cp.boolvar(shape=(b, n), name="sets")

# Constraints

# 1. Each triple has exactly 3 elements
for t in range(b):
    model += (cp.sum(sets[t, :]) == 3)

# 2. Each pair of elements appears in exactly one triple
for i in range(n):
    for j in range(i + 1, n):
        model += (cp.sum([sets[t, i] & sets[t, j] for t in range(b)]) == 1)

# 3. Each element appears in exactly r triples (redundant but strengthens model)
for e in range(n):
    model += (cp.sum(sets[:, e]) == r)

# 4. Symmetry breaking: order triples lexicographically (non-decreasing)
model += cp.LexChainLessEq(sets)

# Solve and print
if model.solve():
    solution = {'sets': sets.value().astype(int).tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
