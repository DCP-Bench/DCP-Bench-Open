
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = label (1..12) at position i (positions are 0..11 around the circle)
x = cp.intvar(1, 12, shape=12, name="x")

# f[i] = successor position when jumping from position i: (i + x[i]) % 12
f = cp.intvar(0, 11, shape=12, name="f")

# Constraints
# x is a permutation of 1..12
model += cp.AllDifferent(x)

# Define successors according to the rule: from position i jump x[i] places clockwise
for i in range(12):
    model += (f[i] == (i + x[i]) % 12)

# Ensure the successor mapping forms a single Hamiltonian cycle (visit all positions)
model += cp.Circuit(f)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
