from cpmpy import *
import json

# Parameters
# Given values
A = 16
B = 2
F = 8
G = 14

# Decision variables
H = intvar(0, 99, name="H")
D = intvar(0, 99, name="D")
K = intvar(0, 99, name="K")
E = intvar(0, 99, name="E")
C = intvar(0, 99, name="C")
I = intvar(0, 99, name="I")

# All variables
variables = [H, D, K, G, E, F, C, I, A, B]

# Model
model = Model()

# All numbers must be different
model += [AllDifferent(variables)]

# Constraints for the puzzle
# B and C should be equal to G and H
model += [(B**2 + C**2) == (G**2 + H**2)]
# A and K to F and E
model += [(A**2 + K**2) == (F**2 + E**2)]
# H and I to C and D
model += [(H**2 + I**2) == (C**2 + D**2)]
# D and C to I and H
model += [(D**2 + C**2) == (I**2 + H**2)]
# C and B to D and A
model += [(C**2 + B**2) == (D**2 + A**2)]
# B and A to C and K
model += [(B**2 + A**2) == (C**2 + K**2)]
# A and F to B and G
model += [(A**2 + F**2) == (B**2 + G**2)]
# F and G to A and B
model += [(F**2 + G**2) == (A**2 + B**2)]
# G and H to F and E
model += [(G**2 + H**2) == (F**2 + E**2)]
# H and I to G and F
model += [(H**2 + I**2) == (G**2 + F**2)]
# I and D to H and G
model += [(I**2 + D**2) == (H**2 + G**2)]
# D and E to I and F
model += [(D**2 + E**2) == (I**2 + F**2)]
# E and K to D and C
model += [(E**2 + K**2) == (D**2 + C**2)]
# K and A to E and D
model += [(K**2 + A**2) == (E**2 + D**2)]

# Solve the model
model.solve()

# Print the solution
solution = {
    "H": H.value(),
    "D": D.value(),
    "K": K.value(),
    "G": G,
    "E": E.value(),
    "C": C.value(),
    "I": I.value(),
    "F": F,
    "A": A,
    "B": B
}
print(json.dumps(solution))