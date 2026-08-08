from cpmpy import *
import json

# Decision Variables
apples = intvar(0, 10000, shape=6, name="apples")  # Apples before each gate and after last gate

# Model
model = Model()

# Constraints
# After passing through 5 gates (before giving to girl), he has 1 apple left
model += (apples[5] == 1)

# For each gate, he gives half his apples plus one (must be integer)
for i in range(5):
    model += (apples[i] % 2 == 0)  # Must be even to give half as integer
    model += (apples[i+1] == apples[i] - (apples[i]//2 + 1))

# Solve
model.solve()

# Print solution
solution = {
    "apples": apples.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script