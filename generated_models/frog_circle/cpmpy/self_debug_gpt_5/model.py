
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# x[pos] = card number at position pos (positions 0..11 around the circle)
x = cp.intvar(1, 12, shape=12, name="x")
# y[pos] = successor position when jumping from pos
y = cp.intvar(0, 11, shape=12, name="y")
# q[pos] is the wrap-around indicator for modulo (0 or 1)
q = cp.intvar(0, 1, shape=12, name="q")

# Constraints
# All cards are a permutation of 1..12
model += cp.AllDifferent(x)

# Successor constraint: y[i] == (i + x[i]) % 12, linearized with q[i] in {0,1}
for i in range(12):
    model += (y[i] == i + x[i] - 12 * q[i])

# The successors form a single Hamiltonian circuit over positions 0..11
model += cp.Circuit(y)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
