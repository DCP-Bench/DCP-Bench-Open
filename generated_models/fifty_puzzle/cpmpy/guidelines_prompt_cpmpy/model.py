
import cpmpy as cp
import json

# Data
values = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=len(values), name="x")

# Constraints
model += cp.sum(x * values) == 50

# Solve and print
if model.solve():
    xval = x.value().tolist()
    chosen = [values[i] for i, v in enumerate(xval) if v == 1]
    solution = {'dummies': chosen}
    print(json.dumps(solution))
else:
    print("No solution found.")
