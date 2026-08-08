
import cpmpy as cp
import json

# Given pairwise sums (sorted, but order doesn't matter for the multiset)
given_sums = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]

# Model definition
model = cp.Model()

# Decision Variables: five bale weights (integers)
# Reasonable bounds: 0..100
bales = cp.intvar(0, 100, shape=5, name="bales")

# Ensure non-decreasing order to break symmetry
model += cp.Increasing(bales)

# All pairwise sums (10 sums for 5 bales)
sums = []
for i in range(5):
    for j in range(i+1, 5):
        sums.append(bales[i] + bales[j])

# The multiset of sums must match the given sums: each given value occurs exactly once
for val in given_sums:
    model += cp.Count(sums, val) == 1

# Solve and print
if model.solve():
    solution = {'bales': bales.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
