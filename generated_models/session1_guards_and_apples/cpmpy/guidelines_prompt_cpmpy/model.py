
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: apples[i] = number of apples before gate i (0-based), apples[5] = after last gate
apples = cp.intvar(0, 1000, shape=6, name="apples")

# Constraints
# After the last gate, he has 0 apples
model += (apples[5] == 0)

# For each gate i from 1 to 5:
# apples[i-1] = 2 * (apples[i] + 1)
# This encodes giving half his apples plus one to the guard
for i in range(1, 6):
    model += (apples[i-1] == 2 * (apples[i] + 1))

# Solve and print
if model.solve():
    solution = {'apples': apples.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
