
import cpmpy as cp
import json

# Data (optional)
n = 12  # Length of the magic sequence
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, n-1, shape=n, name="x")

# Constraints
# For each i in 0..n-1, the number i occurs exactly x[i] times in the sequence
for i in range(n):
    model += (cp.Count(x, i) == x[i])

# Sum of all x[i] equals n (total occurrences equals sequence length)
model += (cp.sum(x) == n)

# Objective (optional)
# No objective; satisfaction problem

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
