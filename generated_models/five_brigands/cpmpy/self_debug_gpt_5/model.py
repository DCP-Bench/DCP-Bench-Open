
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: A, B, C, D, E are integers >= 1
A = cp.intvar(1, 200, name="A")
B = cp.intvar(1, 200, name="B")
C = cp.intvar(1, 200, name="C")
D = cp.intvar(1, 200, name="D")
E = cp.intvar(1, 200, name="E")

# Constraints
# 1) Original total
model += (A + B + C + D + E == 200)

# 2) Scaled total: 12A + 3B + C + D/2 + E/3 = 200
# Multiply by 6 to keep integer arithmetic:
# 72A + 18B + 6C + 3D + 2E = 1200
model += (72*A + 18*B + 6*C + 3*D + 2*E == 1200)

# Solve and print
if model.solve():
    solution = {
        'A': int(A.value()),
        'B': int(B.value()),
        'C': int(C.value()),
        'D': int(D.value()),
        'E': int(E.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
