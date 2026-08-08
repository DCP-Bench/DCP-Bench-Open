
import cpmpy as cp
import json

# Data
l = 9  # Value of l (must be an odd positive integer)
m = (l - 1) // 2
# End of data

# Model definition
model = cp.Model()

# Decision Variables: use binary vars 0/1 and map to -1/+1 via 2*x-1
a_bin = cp.intvar(0, 1, shape=l, name="a_bin")
b_bin = cp.intvar(0, 1, shape=l, name="b_bin")
a = 2 * a_bin - 1
b = 2 * b_bin - 1

# Constraints
# Quadratic PAF constraints: for s = 1..m, PAF(A,s) + PAF(B,s) == -2
for s in range(1, m + 1):
    pafA = cp.sum([a[i] * a[(i + s) % l] for i in range(l)])
    pafB = cp.sum([b[i] * b[(i + s) % l] for i in range(l)])
    model += (pafA + pafB == -2)

# Linear constraints: sums equal to 1
model += (cp.sum(a) == 1)
model += (cp.sum(b) == 1)

# Solve and print
if model.solve():
    a_val = (2 * a_bin.value() - 1).tolist()
    b_val = (2 * b_bin.value() - 1).tolist()
    solution = {'a': a_val, 'b': b_val}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
