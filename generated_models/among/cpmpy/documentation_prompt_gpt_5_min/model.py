
import cpmpy as cp
import json

# Data
n = 7  # Length of x
m = 4  # Number of values
v = [1, 5, 6, 7]  # Values to be among in x
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 7, shape=n, name="x")

# Constraints
# Exactly m variables of x must take a value in the set v
model += cp.Among(x, v) == m

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
