
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# x: permutation of 1..12 representing numbers on the clock in order
x = cp.intvar(1, 12, shape=12, name="x")

# s[i]: sum of triplet starting at position i (i, i+1, i+2) with wrap-around
s = cp.intvar(3, 33, shape=12, name="s")  # min 1+2+3=6, but kept 3..33 to be safe

# M: maximum triplet sum
M = cp.intvar(0, 33, name="M")

# Constraints
model += cp.AllDifferent(x)  # permutation of 1..12

# Triplet sums and linking to M
for i in range(12):
    a = x[i]
    b = x[(i+1) % 12]
    c = x[(i+2) % 12]
    model += (s[i] == a + b + c)
    model += (s[i] <= M)

# Objective: minimize the maximum triplet sum
model.minimize(M)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
