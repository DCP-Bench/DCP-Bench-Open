
import cpmpy as cp
import json

# Define variables
steps = cp.intvar(0, 5, shape=20)

model = cp.Model()

# Constraints
# Each step must be 0, 3, 4, or 5
for s in steps:
    model += cp.InDomain(s, [0, 3, 4, 5])

# Total steps must sum to exactly 20
model += cp.sum(steps) == 20

# Once a 0 is taken, all subsequent steps must be 0
for i in range(19):
    model += (steps[i] == 0).implies(steps[i + 1] == 0)

# Solve and print
if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
