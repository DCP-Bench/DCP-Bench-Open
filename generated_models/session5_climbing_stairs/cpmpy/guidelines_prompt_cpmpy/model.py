
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# steps[i] is the number of steps taken at move i (0 means no move).
steps = cp.intvar(0, 5, shape=20, name="steps")

# Constraints
# Each move must be 3, 4, or 5 steps, or 0 (after finishing).
model += [steps[i] != 1 for i in range(20)]
model += [steps[i] != 2 for i in range(20)]
# Sum of all moves must be exactly 20 steps.
model += cp.sum(steps) == 20
# Once we have a 0 (no move), all subsequent entries must be 0 (trailing zeros).
model += [cp.implies(steps[i] == 0, steps[i+1] == 0) for i in range(19)]

# Solve and print
if model.solve():
    solution = {
        "steps": steps.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
