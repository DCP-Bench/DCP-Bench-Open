from cpmpy import *
import json
from itertools import permutations

# Decision Variables
m = intvar(1, 100, name="m")  # My age
h = intvar(1, 100, name="h")  # Husband's age

# Model
model = Model()

# Define operations as functions that can be applied to variables
def op1(x): return x + 2
def op2(x): return x // 8     # Using integer division
def op3(x): return x - 3
def op4(x): return x * 7

ops = [op1, op2, op3, op4]

# Create all possible permutations of operations
perms = list(permutations(ops))

# Create constraints for m to h transformation
m_to_h = []
for p in perms:
    # Apply operations in correct order (p[0] first, p[1] second, etc.)
    res = p[0](p[1](p[2](p[3](m))))
    m_to_h.append(res == h)

# Create constraints for h to m transformation
h_to_m = []
for p in perms:
    res = p[0](p[1](p[2](p[3](h))))
    h_to_m.append(res == m)

# Add constraints: at least one permutation works for each direction
model += sum(m_to_h) >= 1
model += sum(h_to_m) >= 1

# Solve
model.solve()

# Print solution
solution = {
    "m": m.value(),
    "h": h.value()
}
print(json.dumps(solution))