
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: apples before each of the 5 gates and after the last gate (6 values)
apples = cp.intvar(0, 10000, shape=6, name="apples")

# Constraints:
# For each gate i (0..4), if apples[i] is the number before gate i+1 and apples[i+1] after,
# then apples[i+1] = apples[i]/2 - 1  => apples[i] == 2*(apples[i+1] + 1)
for i in range(5):
    model += (apples[i] == 2 * (apples[i+1] + 1))

# After the last gate he has one apple (which he then gives to the girl, leaving 0)
model += (apples[5] == 1)

# Solve and print
if model.solve():
    solution = {'apples': apples.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
