
import cpmpy as cp
import json

# We want a de Bruijn sequence B(2,4): a cyclic binary sequence of length 2^4 = 16
# such that every binary string of length 4 occurs exactly once as a cyclic substring.

# Model definition
model = cp.Model()

# Decision Variables
de_bruijn = cp.intvar(0, 1, shape=16, name="de_bruijn")   # sequence bits (0/1)
substr = cp.intvar(0, 15, shape=16, name="substr")        # integer encoding of each length-4 substring

# Constraints
# For each position i, substr[i] encodes de_bruijn[i..i+3] (cyclically) as a 4-bit integer
weights = [8, 4, 2, 1]
for i in range(16):
    model += (substr[i] == cp.sum([weights[j] * de_bruijn[(i + j) % 16] for j in range(4)]))

# All 16 substrings must be distinct (cover all 0..15 exactly once)
model += cp.AllDifferent(substr)

# Solve and print
if model.solve():
    solution = {'de_bruijn': de_bruijn.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
