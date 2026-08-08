
import cpmpy as cp
import json

# Data
numbers = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]
n = len(numbers)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: whether each dummy is knocked over (boolean)
dummies = cp.boolvar(shape=n, name="dummies")

# Constraints: sum of numbers on knocked-over dummies must be exactly 50
model += cp.sum([numbers[i] * dummies[i] for i in range(n)]) == 50

# Solve and print
if model.solve():
    # Convert booleans to 0/1 integers as required
    solution = {'dummies': [int(v) for v in dummies.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
