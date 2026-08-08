
import cpmpy as cp
import json

# Data
n = 8
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# X is a permutation of 0..n-1 representing the column positions of marks in each row
X = cp.intvar(0, n-1, shape=n, name="X")

# Constraints
# 1. X is a permutation (all different)
model += cp.AllDifferent(X)

# 2. Difference triangle lines must be all different for each lag l
for l in range(1, n):
    diff_line = [X[i] - X[i + l] for i in range(n - l)]
    model += cp.AllDifferent(diff_line)

# Solve and print
if model.solve():
    solution = {'costas': X.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
