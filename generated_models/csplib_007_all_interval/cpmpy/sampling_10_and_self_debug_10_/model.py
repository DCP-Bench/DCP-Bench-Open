
import cpmpy as cp
import json

# Data
n = 12  # Number of pitch-classes
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, n-1, shape=n, name="x")          # sequence (permutation of 0..n-1)
diffs = cp.intvar(1, n-1, shape=n-1, name="diffs")  # absolute differences 1..n-1

# Constraints
model += cp.AllDifferent(x)        # x is a permutation of 0..n-1
model += cp.AllDifferent(diffs)    # diffs is a permutation of 1..n-1

# Link diffs with absolute differences of consecutive elements
for i in range(n-1):
    model += (diffs[i] == cp.Abs(x[i+1] - x[i]))

# Symmetry breaking to speed up search (optional but helpful):
# Fix the first pitch-class to 0 (we can always add a constant mod n)
model += (x[0] == 0)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist(), 'diffs': diffs.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
