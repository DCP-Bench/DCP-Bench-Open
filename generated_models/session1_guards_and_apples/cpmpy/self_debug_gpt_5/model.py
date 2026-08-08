
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
apples = cp.intvar(0, 100000, shape=6, name="apples")

# Constraints
# After the 5th gate, he has 1 apple to give to the girl
model += (apples[5] == 1)

# Relationship between apples before consecutive gates:
# If A_i is apples before gate i, then after bribing, apples become A_{i+1} = A_i/2 - 1
# This is equivalently A_i = 2*(A_{i+1} + 1), ensuring even counts before each gate
for i in range(5):
    model += (apples[i] == 2 * (apples[i+1] + 1))

# Solve and print
if model.solve():
    solution = {'apples': apples.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
