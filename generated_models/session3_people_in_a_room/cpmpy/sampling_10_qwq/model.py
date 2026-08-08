
import cpmpy as cp
import json

model = cp.Model()

# Decision variables: sequence of 0 (male) and 1 (female)
seq = cp.intvar(0, 1, shape=13, name='sequence')

# Constraints
# Total number of females is 9 (since there are 4 males)
model += (cp.sum(seq) == 9)

# For each step from 1 to 13, ensure 3*Females ≤ 7*Males
for k in range(1, 14):
    current_f = cp.sum(seq[:k])
    males = k - current_f
    model += (3 * current_f <= 7 * males)

# Solve and print
if model.solve():
    solution = {'sequence': seq.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
