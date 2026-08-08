
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
# A, B, F, G are fixed, others are variables
# Numbers are positive integers with at most two digits (1 to 99)
C = cp.intvar(1, 99, name="C")
D = cp.intvar(1, 99, name="D")
E = cp.intvar(1, 99, name="E")
H = cp.intvar(1, 99, name="H")
I = cp.intvar(1, 99, name="I")
K = cp.intvar(1, 99, name="K")

# Fixed variables as constants for convenience
A = A_val
B = B_val
F = F_val
G = G_val

# All numbers must be different
model += cp.AllDifferent([A, B, C, D, E, F, G, H, I, K])

# The sum of squares of any two adjacent numbers equals the sum of squares of the two numbers diametrically opposite
# The circle order is: A, B, C, D, E, F, G, H, I, K
# Adjacent pairs and their opposite pairs:
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

# But the problem states the pairs to check are:
# A and K to F and E
# B and C to G and H
# H and I to C and D
# and so on, with any two adjoining squares in the circle.

# The problem gives examples:
# sum of squares(A,B) = sum of squares(F,E)
# sum of squares(B,C) = sum of squares(G,H)
# sum of squares(H,I) = sum of squares(C,D)
# sum of squares(A,K) = sum of squares(F,E)
# sum of squares(D,E) = sum of squares(I,K)
# sum of squares(E,F) = sum of squares(K,A)
# sum of squares(F,G) = sum of squares(A,B)
# sum of squares(G,H) = sum of squares(B,C)
# sum of squares(I,K) = sum of squares(D,E)

# We will use the pairs as per the problem statement and the circle adjacency:
# The circle is: A-B-C-D-E-F-G-H-I-K-A (circular)
# For each adjacent pair, sum of squares equals sum of squares of opposite pair

# Define the variables in a list for easier indexing
# Index: 0:A,1:B,2:C,3:D,4:E,5:F,6:G,7:H,8:I,9:K
vals = [A, B, C, D, E, F, G, H, I, K]

# Define the pairs of adjacent indices and their opposite pairs
# The circle has 10 squares, opposite pairs are 5 apart
# For i in 0..9, adjacent pair is (i, (i+1)%10)
# Opposite pair is ((i+5)%10, (i+6)%10)
adjacent_pairs = [(i, (i+1)%10) for i in range(10)]
opposite_pairs = [((i+5)%10, (i+6)%10) for i in range(10)]

# Add constraints for sum of squares equality for each adjacent pair and its opposite pair
for i in range(10):
    a1, a2 = adjacent_pairs[i]
    o1, o2 = opposite_pairs[i]
    # sum of squares of adjacent pair == sum of squares of opposite pair
    model += vals[a1]*vals[a1] + vals[a2]*vals[a2] == vals[o1]*vals[o1] + vals[o2]*vals[o2]

# Solve and print
if model.solve():
    solution = {
        'A': int(A),
        'B': int(B),
        'C': int(C.value()),
        'D': int(D.value()),
        'E': int(E.value()),
        'F': int(F),
        'G': int(G),
        'H': int(H.value()),
        'I': int(I.value()),
        'K': int(K.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
