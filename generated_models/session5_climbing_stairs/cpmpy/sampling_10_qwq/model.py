
import cpmpy as cp
import json

n = 20

# Variables
steps = cp.intvar(0, 5, shape=n, name="steps")

model = cp.Model()

# Constraints
# Each step must be either 0 or between 3 and 5 (inclusive)
for s in steps:
    model += [cp.InDomain(s, [0, 3, 4, 5])]

# Total steps must sum to exactly 20
model += (cp.sum(steps) == 20)

# Once a 0 appears, all subsequent steps must also be 0
for i in range(n - 1):
    model += (steps[i] == 0).implies(steps[i + 1] == 0)

# Solve the model
if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
