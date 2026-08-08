
import cpmpy as cp
import numpy as np
import json

# Data
nums = np.array([15, 9, 30, 21, 19, 3, 12, 6, 25, 27], dtype=int)
n = len(nums)
target = 50
# End of data

# Model definition
model = cp.Model()

# Decision Variables
dummies = cp.boolvar(shape=n, name="dummies")

# Constraints
# Sum of selected dummies equals target
model += (cp.sum([nums[i] * dummies[i] for i in range(n)]) == target)

# Objective (none, feasibility problem)

# Solve and print
if model.solve():
    dummies_list = [int(v) for v in dummies.value().tolist()]
    solution = {'dummies': dummies_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
