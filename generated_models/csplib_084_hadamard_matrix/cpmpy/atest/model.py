from cpmpy import *
import json

# Parameters
l = 9  # Value of l (must be an odd positive integer)
m = (l - 1) // 2  # Value of m

# Decision variables
a = intvar(-1, 1, shape=l, name="a")
b = intvar(-1, 1, shape=l, name="b")

# Model
model = Model()

# Linear constraints
model += [sum(a) == 1]
model += [sum(b) == 1]

# Quadratic constraints
for s in range(1, m + 1):
    paf_a = 0
    paf_b = 0
    for i in range(l):
        j = (i + s) % l
        paf_a += a[i] * a[j]
        paf_b += b[i] * b[j]
    model += [paf_a + paf_b == -2]

# Solve the model
model.solve()

# Print the solution
solution = {"a": a.value().tolist(), "b": b.value().tolist()}
print(json.dumps(solution))