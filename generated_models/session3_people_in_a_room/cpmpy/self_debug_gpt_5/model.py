
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# sequence[i] = 0 for male, 1 for female
sequence = cp.intvar(0, 1, shape=13, name="sequence")

# Constraints
# Exactly 9 females (and thus 4 males)
model += (cp.sum(sequence) == 9)

# At any time k, ratio females/males <= 7/3
# Equivalent linear form: 10 * (#females in first k) <= 7 * k
for k in range(1, 14):
    model += (10 * cp.sum(sequence[:k]) <= 7 * k)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
