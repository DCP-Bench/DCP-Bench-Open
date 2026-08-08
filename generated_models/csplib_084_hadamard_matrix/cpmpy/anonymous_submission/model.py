# Import libraries
from cpmpy import *
import json

# Parameters
l = 9  # Value of l (must be an odd positive integer)
m = (l - 1) // 2

# Decision Variables
a = intvar(-1, 1, shape=l, name="a")  # Variables a_1 to a_l
b = intvar(-1, 1, shape=l, name="b")  # Variables b_1 to b_l

# Model
model = Model()

# Constraint: PAF(A,s) + PAF(B,s) = -2 for s=1..m
for s in range(1, m+1):
    PAF_A = sum(a[i] * a[(i+s) % l] for i in range(l))
    PAF_B = sum(b[i] * b[(i+s) % l] for i in range(l))
    model += (PAF_A + PAF_B) == -2

# Constraint: sum of a's = 1
model += sum(a) == 1

# Constraint: sum of b's = 1
model += sum(b) == 1

# Solve
model.solve()

# Print solution
solution = {
    "a": a.value().tolist(),
    "b": b.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script