
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
A = cp.intvar(16, 16, name="A")  # given
B = cp.intvar(2, 2, name="B")    # given
F = cp.intvar(8, 8, name="F")    # given
G = cp.intvar(14, 14, name="G")  # given

# unknowns
C = cp.intvar(1, 99, name="C")
D = cp.intvar(1, 99, name="D")
E = cp.intvar(1, 99, name="E")
H = cp.intvar(1, 99, name="H")
I = cp.intvar(1, 99, name="I")
K = cp.intvar(1, 99, name="K")

# All numbers must be distinct
model += cp.AllDifferent([A, B, C, D, E, F, G, H, I, K])

# Constraint: sum of squares of adjacent equals sum of squares of diametrically opposite
# (A,B) vs (F,G)  -- already holds by the given values, but we include for completeness
model += A*A + B*B == F*F + G*G

# (B,C) vs (G,H)
model += B*B + C*C == G*G + H*H

# (C,D) vs (H,I)
model += C*C + D*D == H*H + I*I

# (D,E) vs (I,K)
model += D*D + E*E == I*I + K*K

# (E,F) vs (K,A)
model += E*E + F*F == K*K + A*A

# Solve and print
if model.solve():
    solution = {
        "A": int(A.value()),
        "B": int(B.value()),
        "C": int(C.value()),
        "D": int(D.value()),
        "E": int(E.value()),
        "F": int(F.value()),
        "G": int(G.value()),
        "H": int(H.value()),
        "I": int(I.value()),
        "K": int(K.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
