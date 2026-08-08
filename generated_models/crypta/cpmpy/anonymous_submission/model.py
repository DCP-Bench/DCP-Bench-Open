from cpmpy import *
import json

# Decision Variables
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

# Model
model = Model()

# All letters must be distinct
model += AllDifferent([A, B, C, D, E, F, G, H, I, J])

# Leading digits cannot be zero
model += (A != 0)
model += (D != 0)
model += (G != 0)

# Define the words
word1 = "BAIJJAJIIAHFCFEBBJEA"
word2 = "DHFGABCDIDBIFFAGFEJE"
result = "GJEGACDDHFAFJBFIHEEF"

# Reverse the words to process from least significant digit
word1 = word1[::-1]
word2 = word2[::-1]
result = result[::-1]

# Create carry variables (one for each column plus one for final carry)
max_len = max(len(word1), len(word2), len(result))
carry = intvar(0, 1, shape=max_len+1, name="carry")

# Create mapping from letters to variables
letter_map = {
    'A': A, 'B': B, 'C': C, 'D': D, 'E': E,
    'F': F, 'G': G, 'H': H, 'I': I, 'J': J
}

# Add column-wise constraints
for i in range(max_len):
    # Get current digits (or 0 if beyond word length)
    d1 = letter_map[word1[i]] if i < len(word1) else 0
    d2 = letter_map[word2[i]] if i < len(word2) else 0
    res = letter_map[result[i]] if i < len(result) else 0
    
    # Add column constraint: d1 + d2 + carry[i] == res + 10*carry[i+1]
    model += (d1 + d2 + carry[i] == res + 10 * carry[i+1])

# Final carry must be 0 (no overflow)
model += (carry[max_len] == 0)

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
    "J": J.value()
}
print(json.dumps(solution))
# End of CPMPy script