
import cpmpy as cp
import json

l = 9
m = (l - 1) // 2

model = cp.Model()

# Decision Variables
a = cp.intvar(-1, 1, shape=l, name="a")
b = cp.intvar(-1, 1, shape=l, name="b")

# Enforce variables to be exactly -1 or 1
for var in a:
    model += cp.InDomain(var, [-1, 1])
for var in b:
    model += cp.InDomain(var, [-1, 1])

# Linear constraints
model += (cp.sum(a) == 1)
model += (cp.sum(b) == 1)

# Quadratic constraints for each s from 1 to m
for s in range(1, m + 1):
    paf_a = cp.sum(a[i] * a[(i + s) % l] for i in range(l))
    paf_b = cp.sum(b[i] * b[(i + s) % l] for i in range(l))
    model += (paf_a + paf_b == -2)

# Solve and print
if model.solve():
    solution = {
        'a': a.value().tolist(),
        'b': b.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
