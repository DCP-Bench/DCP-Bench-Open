
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
holes = cp.intvar(3, 5, shape=18, name="holes")

# Constraints
model += (cp.sum(holes) == 72)

# Solve and print
if model.solve():
    solution = {'holes': holes.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
