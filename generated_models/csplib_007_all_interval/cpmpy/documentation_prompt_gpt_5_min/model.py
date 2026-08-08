
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
model += diffs == cp.Abs(x[1:] - x[:-1])

# Symmetry breaking: fix first element to 0 (we can always add a constant mod n),
# and force second element < last element to break reversal symmetry
model += x[0] == 0
model += x[1] < x[-1]

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist(), 'diffs': diffs.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
