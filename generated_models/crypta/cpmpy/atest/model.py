from cpmpy import *
import json

# Decision variables
A = intvar(0, 9, name="A")
B = intvar(0, 9, name="B")
C = intvar(0, 9, name="C")
D = intvar(0, 9, name="D")
E = intvar(0, 9, name="E")
F = intvar(0, 9, name="F")
G = intvar(0, 9, name="G")
H = intvar(0, 9, name="H")
I = intvar(0, 9, name="I")
J = intvar(0, 9, name="J")

# All letters must be distinct digits
model = Model([
    AllDifferent([A, B, C, D, E, F, G, H, I, J])
])

# Define the numbers using a list of digits and cumulative sum
# First number: B A I J J A J I I A H F C F E B B J E A
digits1 = [B, A, I, J, J, A, J, I, I, A, H, F, C, F, E, B, B, J, E, A]
# Second number: D H F G A B C D I D B I F F A G F E J E
digits2 = [D, H, F, G, A, B, C, D, I, D, B, I, F, F, A, G, F, E, J, E]
# Result number: G J E G A C D D H F A F J B F I H E E F
digits3 = [G, J, E, G, A, C, D, D, H, F, A, F, J, B, F, I, H, E, E, F]

# Compute the sum using positional weights (powers of 10)
num1 = sum([digits1[i] * (10 ** (19 - i)) for i in range(20)])
num2 = sum([digits2[i] * (10 ** (19 - i)) for i in range(20)])
num3 = sum([digits3[i] * (10 ** (19 - i)) for i in range(20)])

# The sum of the two numbers must equal the third number
model += [num1 + num2 == num3]

# Solve the model
model.solve()

# Print the solution
solution = {
    "H": H.value(),
    "D": D.value(),
    "J": J.value(),
    "G": G.value(),
    "E": E.value(),
    "C": C.value(),
    "I": I.value(),
    "F": F.value(),
    "A": A.value(),
    "B": B.value()
}
print(json.dumps(solution))