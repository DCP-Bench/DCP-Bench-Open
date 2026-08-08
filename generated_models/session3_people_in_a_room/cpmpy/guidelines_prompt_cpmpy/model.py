
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: 0=male, 1=female for each of the 13 positions
x = cp.intvar(0, 1, shape=13, name="x")

# Constraint: exactly 9 females (and hence 4 males)
model += cp.sum(x) == 9

# Prefix constraints: for any prefix of length k+1, 
# number of females f and males m satisfy 3*f <= 7*m
for k in range(13):
    f = cp.sum(x[:k+1])
    m = (k+1) - f
    model += 3 * f <= 7 * m

# Solve and print
if model.solve():
    solution = {"sequence": x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
