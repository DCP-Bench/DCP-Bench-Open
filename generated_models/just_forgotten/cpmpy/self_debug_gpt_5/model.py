
import cpmpy as cp
import json

# Data
guesses = [
    [9,4,6,2,1,5,7,8,3,0],
    [8,6,0,4,3,9,1,2,5,7],
    [1,6,4,0,2,9,7,8,5,3],
    [6,8,2,4,3,1,9,0,7,5]
]
n = 10
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 9, shape=n, name="x")

# Constraints
# x is a permutation of 0..9
model += cp.AllDifferent(x)

# For each guess, exactly 4 positions match the true account number
for g in guesses:
    model += (cp.sum([x[i] == g[i] for i in range(n)]) == 4)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
