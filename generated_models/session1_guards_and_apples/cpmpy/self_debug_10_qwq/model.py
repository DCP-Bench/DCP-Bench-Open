
import cpmpy as cp
import json

model = cp.Model()

apples = cp.intvar(0, 1000, shape=6, name="apples")

# Constraints
model += (apples[5] == 1)  # After last gate, he has 1 apple to give to the girl

for i in range(5):
    # Each apples[i] must be even and at least 2
    model += (apples[i] % 2 == 0)
    model += (apples[i] >= 2)
    # The next apples value after the gate
    model += (apples[i+1] == (apples[i] // 2) - 1)

if model.solve():
    solution = {'apples': apples.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
