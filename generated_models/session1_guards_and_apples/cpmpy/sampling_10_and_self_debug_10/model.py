
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# apples[i] = number of apples before gate i (0 to 4), apples[5] = apples after last gate
apples = cp.intvar(0, 1000, shape=6, name="apples")

# Constraints
# After giving bribe at each gate: apples[i+1] = apples[i] - (half of apples[i] + 1)
# Since the bribe is half of apples[i] plus one, and must be integer,
# apples[i] must be even (because half must be integer)
for i in range(5):
    # half of apples[i] plus one is integer, so apples[i] must be even
    model += (apples[i] % 2 == 0)
    # apples[i+1] = apples[i] - (apples[i]//2 + 1)
    model += (apples[i+1] == apples[i] - (apples[i] // 2 + 1))

# After last gate, no apples left
model += (apples[5] == 0)

# Solve and print
if model.solve():
    solution = {'apples': apples.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
