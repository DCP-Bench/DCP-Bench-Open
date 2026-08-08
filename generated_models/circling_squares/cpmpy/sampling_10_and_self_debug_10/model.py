
import cpmpy as cp
import json

# Given fixed values
A_val = 16
B_val = 2
F_val = 8
G_val = 14

# Model definition
model = cp.Model()

# Decision Variables: The 10 squares A, B, C, D, E, F, G, H, I, K
# A, B, F, G are fixed
# The others are variables with domain 1..99 (two figures max)
# We use 1..99 as domain since fractions are not allowed and no more than two figures
A = cp.intvar(A_val, A_val, name="A")
B = cp.intvar(B_val, B_val, name="B")
C = cp.intvar(1, 99, name="C")
D = cp.intvar(1, 99, name="D")
E = cp.intvar(1, 99, name="E")
F = cp.intvar(F_val, F_val, name="F")
G = cp.intvar(G_val, G_val, name="G")
H = cp.intvar(1, 99, name="H")
I = cp.intvar(1, 99, name="I")
K = cp.intvar(1, 99, name="K")

# All numbers must be different
model += cp.AllDifferent([A, B, C, D, E, F, G, H, I, K])

# The sum of squares of any two adjacent numbers equals the sum of squares of the two numbers diametrically opposite
# The circle is: A-B-C-D-E-F-G-H-I-K (10 squares)
# Adjacents pairs and their opposite pairs:
# (A,B) opposite (F,E)
# (B,C) opposite (G,H)
# (C,D) opposite (H,I)
# (D,E) opposite (I,K)
# (E,F) opposite (K,A)
# (F,G) opposite (A,B)
# (G,H) opposite (B,C)
# (H,I) opposite (C,D)
# (I,K) opposite (D,E)
# (K,A) opposite (E,F)

# The problem states the pairs to check are:
# B and C equal to G and H
model += B*B + C*C == G*G + H*H
# A and K equal to F and E
model += A*A + K*K == F*F + E*E
# H and I equal to C and D
model += H*H + I*I == C*C + D*D
# The example given: A and B equal to F and G (actually A and B equal to F and E in problem statement, but example is A=16, B=2, F=8, G=14)
# The problem states: sum of squares of any two adjacent numbers equals sum of squares of diametrically opposite two numbers.
# The example given is A and B opposite F and G, but problem states A and B opposite F and E.
# The example given is 16 and 2 (A and B) sum squares = 260, and 14 and 8 (G and F) sum squares = 260.
# So we add this constraint:
model += A*A + B*B == F*F + G*G
# Also H and I equal to C and D (already added)
# B and C equal to G and H (already added)
# A and K equal to F and E (already added)
# H and I equal to C and D (already added)

# Also, the problem states "and so on, with any two adjoining squares in the circle."
# So we add the remaining pairs:
# D and E equal to I and K
model += D*D + E*E == I*I + K*K
# E and F equal to K and A
model += E*E + F*F == K*K + A*A
# F and G equal to A and B (already added as A and B == F and G)
# G and H equal to B and C (already added as B and C == G and H)
# H and I equal to C and D (already added)
# I and K equal to D and E (already added as D and E == I and K)
# K and A equal to E and F (already added as E and F == K and A)

# So all pairs are covered.

# Solve and print
if model.solve():
    solution = {
        'A': int(A.value()),
        'B': int(B.value()),
        'C': int(C.value()),
        'D': int(D.value()),
        'E': int(E.value()),
        'F': int(F.value()),
        'G': int(G.value()),
        'H': int(H.value()),
        'I': int(I.value()),
        'K': int(K.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
