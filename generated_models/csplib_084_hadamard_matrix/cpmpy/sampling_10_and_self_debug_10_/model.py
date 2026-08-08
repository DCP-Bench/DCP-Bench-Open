
import cpmpy as cp
import json

# Data
l = 9
m = (l - 1) // 2
# End of data

# Model definition
model = cp.Model()

# Decision Variables: vectors a and b of length l with domain -1 or 1
a = cp.intvar(-1, 1, shape=l, name="a")
b = cp.intvar(-1, 1, shape=l, name="b")

# Exclude 0 so variables are restricted to {-1, 1}
for i in range(l):
    model += (a[i] != 0)
    model += (b[i] != 0)

# Quadratic constraints: for s = 1..m, PAF(A,s) + PAF(B,s) == -2
for s in range(1, m + 1):
    # periodic autocorrelation for A at shift s
    paf_a = cp.sum([a[i] * a[(i + s) % l] for i in range(l)])
    paf_b = cp.sum([b[i] * b[(i + s) % l] for i in range(l)])
    model += (paf_a + paf_b == -2)

# Linear constraints: sums equal 1
model += (cp.sum(a) == 1)
model += (cp.sum(b) == 1)

# Solve and print
if model.solve():
    solution = {'a': a.value().tolist(), 'b': b.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
