import cpmpy as cp
import json

# Circling the Squares Problem
# Place different numbers in 10 squares arranged in a circle such that
# the sum of squares of any two adjacent numbers equals the sum of squares
# of the two numbers diametrically opposite to them.
# Given: A=16, B=2, F=8, G=14

# Decision variables for unknown positions
C = cp.intvar(0, 99, name="C")
D = cp.intvar(0, 99, name="D") 
E = cp.intvar(0, 99, name="E")
H = cp.intvar(0, 99, name="H")
I = cp.intvar(0, 99, name="I")
K = cp.intvar(0, 99, name="K")

model = cp.Model()

# All numbers must be different
all_vars = [C, D, E, H, I, K]
model += cp.AllDifferent(all_vars)

# Ensure unknowns don't equal known values
for var in all_vars:
    model += var != 16  # A
    model += var != 2   # B  
    model += var != 8   # F
    model += var != 14  # G

# Circle arrangement: A -> B -> C -> D -> E -> F -> G -> H -> I -> K -> A
# Adjacent pairs and their diametric opposites must have equal sum of squares:
# A² + B² = F² + G² (already satisfied: 260 = 260)
# B² + C² = G² + H²
# C² + D² = H² + I²
# D² + E² = I² + K²
# E² + F² = K² + A²

model += 2**2 + C**2 == 14**2 + H**2   # B² + C² = G² + H²
model += C**2 + D**2 == H**2 + I**2    # C² + D² = H² + I²
model += D**2 + E**2 == I**2 + K**2    # D² + E² = I² + K²
model += E**2 + 8**2 == K**2 + 16**2   # E² + F² = K² + A²

if model.solve():
    solution = {
        "A": 16,
        "B": 2,
        "C": C.value(),
        "D": D.value(),
        "E": E.value(),
        "F": 8,
        "G": 14,
        "H": H.value(),
        "I": I.value(),
        "K": K.value()
    }
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))