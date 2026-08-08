
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# apples[i] = number of apples before gate i (0 to 4), apples[5] = apples after last gate
apples = cp.intvar(0, 1000, shape=6, name="apples")

# Constraints
# After last gate, no apples left
model += (apples[5] == 0)

# For each gate i in 0..4:
# The boy gives half of his apples plus one to the guard (integer number)
# So apples[i] - (apples[i]//2 + 1) = apples[i+1]
# Also, apples[i]//2 + 1 must be integer, which is always true since apples[i] is integer
for i in range(5):
    # The number given to guard is half of apples[i] plus one, integer
    # So apples[i] must be even or odd, but the given number must be integer
    # The given number = apples[i]//2 + 1
    model += (apples[i+1] == apples[i] - (apples[i]//2 + 1))
    # The number given must be >= 0 and apples[i+1] >= 0
    model += (apples[i+1] >= 0)
    model += ((apples[i]//2 + 1) >= 0)

# The boy must have at least 1 apple before first gate to give
model += (apples[0] >= 1)

# Solve and print
if model.solve():
    solution = {'apples': apples.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
