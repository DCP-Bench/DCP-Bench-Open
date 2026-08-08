
import cpmpy as cp
import json
import numpy as np

# Data
numbers = np.array([15, 9, 30, 21, 19, 3, 12, 6, 25, 27])

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=len(numbers), name='x')

# Constraints
model += (cp.sum(numbers * x) == 50)

# Solve and print
if model.solve():
    selected = numbers[x.value() == 1].tolist()
    solution = {'dummies': selected}
    print(json.dumps(solution))
else:
    print("No solution found.")
