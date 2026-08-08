
import cpmpy as cp
import json
from collections import Counter

# Data
pair_sums = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]
counts = Counter(pair_sums)
vals = sorted(counts.keys())
occ = [counts[v] for v in vals]
n_bales = 5

# Model definition
model = cp.Model()

# Decision Variables
bales = cp.intvar(1, 100, shape=n_bales, name="bales")  # weights of the 5 bales
pairs = [(i, j) for i in range(n_bales) for j in range(i+1, n_bales)]
s = cp.intvar(min(pair_sums), max(pair_sums), shape=len(pairs), name="pair_sums")

# Constraints
# Symmetry breaking: non-decreasing order of bales
model += cp.Increasing(bales)

# Pair sums equal to sums of bales
for k, (i, j) in enumerate(pairs):
    model += (s[k] == bales[i] + bales[j])

# Enforce that the multiset of pair sums matches exactly the given list
# 1) Each sum must be one of the given values
for k in range(len(pairs)):
    model += cp.InDomain(s[k], vals)
# 2) Global cardinality counts must match the given occurrences
model += cp.GlobalCardinalityCount(s, vals, occ)

# Solve and print
if model.solve():
    solution = {'bales': bales.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
