
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: each brigand has at least 1 and at most 200 doubloons
A = cp.intvar(1, 200, name="A")  # Alfonso
B = cp.intvar(1, 200, name="B")  # Benito
C = cp.intvar(1, 200, name="C")  # Carlos
D = cp.intvar(1, 200, name="D")  # Diego
E = cp.intvar(1, 200, name="E")  # Esteban

# Constraints
# Total doubloons is 200
model += (A + B + C + D + E == 200)

# If scaled amounts (12A, 3B, 1C, 1/2 D, 1/3 E) sum to 200.
# Multiply by 6 to avoid fractions: 72A + 18B + 6C + 3D + 2E = 1200
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
