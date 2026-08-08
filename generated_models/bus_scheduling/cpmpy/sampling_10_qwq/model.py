
import cpmpy as cp
import json

# Input data
demands = [4, 8, 10, 7, 12, 4]

# Model definition
model = cp.Model()

# Decision Variables: x[i] is the number of buses starting at interval i
x = cp.intvar(0, 100, shape=6, name="x")

# Constraints
for j in range(6):
    prev = (j - 1) % 6
    model += (x[prev] + x[j] >= demands[j])

# Objective: minimize total buses
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
