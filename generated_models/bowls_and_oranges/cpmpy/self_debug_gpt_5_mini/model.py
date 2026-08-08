
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: 9 positions (bowls) between 1 and 40
x = cp.intvar(1, 40, shape=9, name="x")

# Constraints
# Enforce strictly increasing order to break symmetry (and thus AllDifferent)
model += cp.IncreasingStrict(x)

# No three oranges in arithmetic progression:
# For all i < j < k: 2*x[j] != x[i] + x[k]
for i in range(9):
    for j in range(i+1, 9):
        for k in range(j+1, 9):
            model += (2 * x[j] != x[i] + x[k])

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
