
import cpmpy as cp
import json

# Data
l = 9  # Value of l (must be an odd positive integer)
m = (l - 1) // 2

# Model definition
model = cp.Model()

# Decision Variables
# Variables a and b with domain {-1, +1}
a = cp.intvar(-1, 1, shape=l, name="a")
b = cp.intvar(-1, 1, shape=l, name="b")

# Constraints
# All variables must be either -1 or +1 (already ensured by domain)

# Quadratic constraints: PAF(A, s) + PAF(B, s) = -2 for s=1..m
# PAF(A, s) = sum_{i=1}^l a_i * a_{(i+s) mod l}
# PAF(B, s) = sum_{i=1}^l b_i * b_{(i+s) mod l}
for s in range(1, m + 1):
    paf_a = cp.sum([a[i] * a[(i + s) % l] for i in range(l)])
    paf_b = cp.sum([b[i] * b[(i + s) % l] for i in range(l)])
    model += (paf_a + paf_b == -2)

# Linear constraints: sum of a_i = 1 and sum of b_i = 1
model += (cp.sum(a) == 1)
model += (cp.sum(b) == 1)

# Solve and print
if model.solve():
    solution = {'a': a.value().tolist(), 'b': b.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
