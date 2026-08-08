
import cpmpy as cp
import json

# Data
n = 5
m = 3
v = [1, 5, 8]

# Model definition
model = cp.Model()

# Decision Variables
# x variables can take values in v or outside; we assume domain as min and max of v for simplicity plus some range
# but problem does not restrict domain, so let's choose domain from min(v) to max(v) plus some slack
# For clarity, let's allow values from min(v) to max(v) (1 to 8)
x = cp.intvar(1, 8, shape=n, name="x")

# Constraints
# Exactly m variables in x take one of the values in v
# Count how many variables in x take values in v
# cp.Count counts number of occurrences of a single value; here we want number of variables in x belonging to v
# So we use cp.Among
model += cp.Among(x, v) == m

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
