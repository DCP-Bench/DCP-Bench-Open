
import cpmpy as cp
import json

# Define variables for the unknown numbers
C = cp.intvar(1, 99, name="C")
D = cp.intvar(1, 99, name="D")
E = cp.intvar(1, 99, name="E")
H = cp.intvar(1, 99, name="H")
I = cp.intvar(1, 99, name="I")
K = cp.intvar(1, 99, name="K")

model = cp.Model()

# Constraints based on the problem's conditions
model += (C**2 - H**2) == 192  # B² + C² = G² + H² (B=2, G=14)
model += (C**2 + D**2) == (H**2 + I**2)  # C² + D² = H² + I²
model += (D**2 + E**2) == (I**2 + K**2)  # D² + E² = I² + K²
model += (E**2 - K**2) == 192  # E² + F² = K² + A² (F=8, A=16)

# Ensure variables are not already used numbers (2, 8, 14, 16)
for var in [C, D, E, H, I, K]:
    model += var != 2
    model += var != 8
    model += var != 14
    model += var != 16

# All variables must be distinct
model += cp.AllDifferent([C, D, E, H, I, K])

# Solve and print the result
if model.solve():
    solution = {
        'A': 16,
        'B': 2,
        'C': int(C.value()),
        'D': int(D.value()),
        'E': int(E.value()),
        'F': 8,
        'G': 14,
        'H': int(H.value()),
        'I': int(I.value()),
        'K': int(K.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
