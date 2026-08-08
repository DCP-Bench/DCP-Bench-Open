
import cpmpy as cp
import json

# Data
n = 20
m1 = 3
m2 = 5
# allowed step sizes are 3,4,5 and 0 for "no move" after reaching the top
allowed = [0, 3, 4, 5]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: sequence of n moves (each either 0,3,4,5)
steps = cp.intvar(0, m2, shape=n, name="steps")

# Constraints
# Each move must be in the allowed set {0,3,4,5}
for i in range(n):
    model += cp.InDomain(steps[i], allowed)

# Total sum of steps must equal n (reach the top exactly)
model += cp.sum(steps) == n

# Once a 0 occurs (meaning we've reached the top), all following moves must be 0
for i in range(n - 1):
    model += (steps[i] == 0).implies(steps[i + 1] == 0)

# Solve and print
if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
