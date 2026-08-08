
import cpmpy as cp
import json

# Data
numbers = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]

# Model definition
model = cp.Model()

# Decision Variables: binary variables indicating if a dummy is knocked over (1) or not (0)
dummies = cp.boolvar(shape=len(numbers), name="dummies")

# Constraints
# The sum of the numbers on the knocked down dummies must be exactly 50
model += (cp.sum([dummies[i] * numbers[i] for i in range(len(numbers))]) == 50)

# Solve and print
if model.solve():
    solution = {'dummies': [int(x) for x in dummies.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
