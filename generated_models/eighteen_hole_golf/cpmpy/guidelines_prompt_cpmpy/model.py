
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: 18 holes, each with length 3, 4, or 5
holes = cp.IntVar(3, 5, shape=18, name="holes")

# Constraint: total length of the course must be 72
model += cp.sum(holes) == 72

# Solve and print
if model.solve():
    solution = {'holes': holes.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
