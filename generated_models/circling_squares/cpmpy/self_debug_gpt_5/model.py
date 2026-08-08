
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables (each is a distinct integer between 1 and 99)
A = cp.intvar(1, 99, name="A")
B = cp.intvar(1, 99, name="B")
C = cp.intvar(1, 99, name="C")
D = cp.intvar(1, 99, name="D")
E = cp.intvar(1, 99, name="E")
F = cp.intvar(1, 99, name="F")
G = cp.intvar(1, 99, name="G")
H = cp.intvar(1, 99, name="H")
I = cp.intvar(1, 99, name="I")
K = cp.intvar(1, 99, name="K")

x = [A, B, C, D, E, F, G, H, I, K]

# Squares auxiliary variables
S = cp.intvar(1, 9801, shape=10, name="S")  # squares from 1^2 to 99^2
# Table mapping value -> square(value)
sq_table = [(v, v*v) for v in range(1, 100)]
for i in range(10):
    model += cp.Table([x[i], S[i]], sq_table)

# Constraints
# 1) All numbers are different
model += cp.AllDifferent(x)

# 2) Fix given values
model += (A == 16)
model += (B == 2)
model += (F == 8)
model += (G == 14)

# 3) For any two adjacent numbers, sum of squares equals sum of squares of diametrically opposite adjacent pair
#    Indices modulo 10; opposite of (i, i+1) is (i+5, i+6)
n = 10
for i in range(n):
    model += (S[i] + S[(i+1) % n] == S[(i+5) % n] + S[(i+6) % n])

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
