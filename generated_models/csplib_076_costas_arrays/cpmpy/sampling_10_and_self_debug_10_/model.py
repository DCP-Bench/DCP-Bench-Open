
import cpmpy as cp
import json

# Data
n = 8
# End of data

# Model definition
model = cp.Model()

# Decision Variables
X = cp.intvar(1, n, shape=n, name="X")  # permutation representing the Costas array

# Constraints
model += cp.AllDifferent(X)

# Build the difference triangle and post all-different on each row
diffs = []
for l in range(1, n):
    # row for difference of length l: X[i] - X[i+l] for i = 0..n-l-1
    dl = cp.intvar(-(n-1), n-1, shape=(n - l,), name=f"d_{l}")
    for i in range(n - l):
        model += dl[i] == X[i] - X[i + l]
    model += cp.AllDifferent(dl)
    diffs.append(dl)

# Solve and print
if model.solve():
    solution = {'costas': X.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
