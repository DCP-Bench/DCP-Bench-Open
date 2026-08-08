
import cpmpy as cp
import json

# Data
l = 9  # must be odd
# End of data

# Model definition
model = cp.Model()

# Decision Variables: a[0..l-1], b[0..l-1] in {-1, +1}
a = cp.intvar(-1, 1, shape=(l,), name="a")
b = cp.intvar(-1, 1, shape=(l,), name="b")

# m = (l - 1) // 2
m = (l - 1) // 2

# Quadratic autocorrelation constraints:
# For each shift s = 1..m: PAF(A,s) + PAF(B,s) == -2
for s in range(1, m + 1):
    # build PAF(A, s) = sum_i a[i] * a[(i+s)%l]
    terms_a = [a[i] * a[(i + s) % l] for i in range(l)]
    # build PAF(B, s) = sum_i b[i] * b[(i+s)%l]
    terms_b = [b[i] * b[(i + s) % l] for i in range(l)]
    model += cp.sum(terms_a) + cp.sum(terms_b) == -2

# Linear sum constraints: sum(a) = 1, sum(b) = 1
model += cp.sum(a) == 1
model += cp.sum(b) == 1

# Solve and print
if model.solve():
    solution = {
        'a': a.value().tolist(),
        'b': b.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
