
import cpmpy as cp
import json
import numpy as np

# Data
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]
A_np = np.array(A, dtype=int)
n = len(A)

# Model definition
model = cp.Model()

# Decision Variables
s = cp.boolvar(shape=n, name="s")  # in S
t = cp.boolvar(shape=n, name="t")  # in T

# Constraints
# Disjoint non-empty subsets
model += (s + t <= 1)
model += (cp.sum(s) >= 1)
model += (cp.sum(t) >= 1)

# Equal sums
model += (cp.sum(A_np * s) == cp.sum(A_np * t))

# Solve and print
if model.solve():
    in_S = [int(v) for v in s.value().tolist()]
    in_T = [int(v) for v in t.value().tolist()]
    solution = {
        'in_S': in_S,
        'in_T': in_T
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
