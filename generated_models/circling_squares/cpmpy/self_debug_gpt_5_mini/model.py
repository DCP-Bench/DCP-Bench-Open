
import cpmpy as cp
import json

# Data
# Positions in order around the circle: A, B, C, D, E, F, G, H, I, K
# Index mapping: 0=A,1=B,2=C,3=D,4=E,5=F,6=G,7=H,8=I,9=K

# Model definition
model = cp.Model()

# Decision Variables
# Allow integers with at most two digits (0..99)
x = cp.intvar(0, 99, shape=10, name="x")   # A..K
# auxiliary variables for squares (0..99^2)
s = cp.intvar(0, 99*99, shape=10, name="s")  # squares of x

# Precompute table mapping value -> its square for domain 0..99
table = [[v, v*v] for v in range(0, 100)]

# Constraints
# All numbers different
model += cp.AllDifferent(x)

# Given fixed values: A=16, B=2, F=8, G=14
model += (x[0] == 16)  # A
model += (x[1] == 2)   # B
model += (x[5] == 8)   # F
model += (x[6] == 14)  # G

# Link each x[i] with its square s[i] via Table constraint
for i in range(10):
    model += cp.Table([x[i], s[i]], table)

# For each adjacent pair, sum of their squares equals sum of squares of diametrically opposite pair.
# For i in 0..9: (i, i+1) opposite (i+5, i+6) with indices modulo 10
for i in range(10):
    a = i
    b = (i+1) % 10
    c = (i+5) % 10
    d = (i+6) % 10
    model += (s[a] + s[b] == s[c] + s[d])

# No objective (just find a feasible arrangement)

# Solve and print
if model.solve():
    solution = {
        'A': int(x[0].value()),
        'B': int(x[1].value()),
        'C': int(x[2].value()),
        'D': int(x[3].value()),
        'E': int(x[4].value()),
        'F': int(x[5].value()),
        'G': int(x[6].value()),
        'H': int(x[7].value()),
        'I': int(x[8].value()),
        'K': int(x[9].value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
