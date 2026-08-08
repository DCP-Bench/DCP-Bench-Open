
import cpmpy as cp
import json

# Data (optional)
n = 7  # Length of x
m = 4  # Number of values
v = [1, 5, 6, 7]  # Values to be among in x
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 7, shape=n, name="x")

# Constraints
# Exactly m values in x must be in the set v; others are within domain [0,7]
model += (cp.Among(x, v) == m)

# Objective (optional)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
