from cpmpy import *
import json

# Decision Variables
# Variables for each position in the circle (A-K, skipping J)
A = intvar(1, 99, name="A")
B = intvar(1, 99, name="B")
C = intvar(1, 99, name="C")
D = intvar(1, 99, name="D")
E = intvar(1, 99, name="E")
F = intvar(1, 99, name="F")
G = intvar(1, 99, name="G")
H = intvar(1, 99, name="H")
I = intvar(1, 99, name="I")
K = intvar(1, 99, name="K")

# Model
model = Model()

# Fixed values from the problem statement
model += A == 16
model += B == 2
model += F == 8
model += G == 14

# All variables must be distinct
model += AllDifferent([A, B, C, D, E, F, G, H, I, K])

# Adjacent pairs must have sum of squares equal to their diametrically opposite pair
# Assuming the circle order is A, B, C, D, E, F, G, H, I, K
model += (A**2 + B**2) == (F**2 + G**2)  # Given in problem
model += (B**2 + C**2) == (G**2 + H**2)
model += (C**2 + D**2) == (H**2 + I**2)
model += (D**2 + E**2) == (I**2 + K**2)
model += (E**2 + F**2) == (K**2 + A**2)
model += (F**2 + G**2) == (A**2 + B**2)  # Same as first constraint
model += (G**2 + H**2) == (B**2 + C**2)
model += (H**2 + I**2) == (C**2 + D**2)
model += (I**2 + K**2) == (D**2 + E**2)
model += (K**2 + A**2) == (E**2 + F**2)

# Solve
model.solve()

# Print solution in alphabetical order
solution = {
    "A": A.value(),
    "B": B.value(),
    "C": C.value(),
    "D": D.value(),
    "E": E.value(),
    "F": F.value(),
    "G": G.value(),
    "H": H.value(),
    "I": I.value(),
    "K": K.value()
}
print(json.dumps(solution))
# End of CPMPy script