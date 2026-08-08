
import cpmpy as cp
import json

# Data
num_bowls = 40
num_oranges = 9

# Model definition
model = cp.Model()

# Decision Variables
# x[i] is the bowl index (1..40) of the i-th orange, strictly increasing to avoid duplicates and enforce order
x = cp.intvar(1, num_bowls, shape=num_oranges, name="x")

# Constraints
# Strictly increasing ensures no more than one orange per bowl
model += cp.IncreasingStrict(x)

# No three-term arithmetic progression: for all i<j<k, 2*x[j] != x[i] + x[k]
for i in range(num_oranges):
    for j in range(i+1, num_oranges):
        for k in range(j+1, num_oranges):
            model += (2 * x[j] != x[i] + x[k])

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
