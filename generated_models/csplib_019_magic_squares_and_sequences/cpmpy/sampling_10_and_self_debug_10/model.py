
import cpmpy as cp
import json

# Data
n = 12
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, n-1, shape=n, name="x")

# Constraints
# For each i, x[i] is the count of i in the sequence x
for i in range(n):
    model += (cp.Count(x, i) == x[i])

# The sum of all x[i] must be n (length of the sequence)
model += (cp.sum(x) == n)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
