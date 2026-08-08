
import cpmpy as cp
import json

# Given values
A = 16
B = 2
F = 8
G = 14

# Variables to find: C, D, E, H, I, K
forbidden = {2, 8, 14, 16}

# Define variables
C = cp.IntVar(1, 99, name="C")
D = cp.IntVar(1, 99, name="D")
E = cp.IntVar(1, 99, name="E")
H = cp.IntVar(1, 99, name="H")
I = cp.IntVar(1, 99, name="I")
K = cp.IntVar(1, 99, name="K")

variables = [C, D, E, H, I, K]

# Initialize model
model = cp.Model()

# Constraints: variables not in forbidden and distinct
for var in variables:
    model += [var != val for val in forbidden]
model += cp.AllDifferent(variables)

# Equations based on the problem's constraints
model += (C*C - H*H == 192)
model += (I*I - D*D == 192)
model += (E*E - K*K == 192)

# Solve the model
if model.solve():
    solution = {
        'A': A,
        'B': B,
        'C': int(C.value()),
        'D': int(D.value()),
        'E': int(E.value()),
        'F': F,
        'G': G,
        'H': int(H.value()),
        'I': int(I.value()),
        'K': int(K.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
