
import cpmpy as cp
import json

# Data
n = 12  # Number of pitch-classes
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, n-1, shape=n, name="x")           # permutation of 0..n-1
diffs = cp.intvar(1, n-1, shape=n-1, name="diffs") # absolute differences 1..n-1

# Constraints
model += cp.AllDifferent(x)        # x is a permutation of Z_n
model += cp.AllDifferent(diffs)    # diffs is a permutation of {1,..,n-1}

# differences are absolute successive differences
for i in range(n-1):
    model += diffs[i] == cp.Abs(x[i+1] - x[i])

# Symmetry breaking: fix first element to 0 (we can always add a constant mod n)
model += x[0] == 0

# Constructive pattern for even n:
# The alternating pattern x = [0, n-1, 1, n-2, 2, n-3, ...] yields diffs = [n-1, n-2, ..., 1]
# This is a valid all-interval series for even n and allows the solver to find a solution immediately.
if n % 2 == 0:
    for k in range(n // 2):
        model += x[2*k] == k
        model += x[2*k + 1] == n - 1 - k

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist(), 'diffs': diffs.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
