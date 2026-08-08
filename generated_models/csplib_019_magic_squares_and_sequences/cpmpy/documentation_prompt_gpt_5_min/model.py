
import cpmpy as cp
import json

# Data
n = 12  # Length of the magic sequence
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, n-1, shape=n, name="x")

# Constraints
# For each i, the number i must occur exactly x[i] times in the sequence x
model += [cp.Count(x, i) == x[i] for i in range(n)]
# The total number of entries is n (redundant but helps propagation)
model += cp.sum(x) == n

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
