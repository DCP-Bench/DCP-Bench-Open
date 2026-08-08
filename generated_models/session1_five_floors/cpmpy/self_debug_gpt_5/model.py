
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: floors 1 (lowest) to 5 (highest)
B = cp.intvar(1, 5, name="B")
C = cp.intvar(1, 5, name="C")
F = cp.intvar(1, 5, name="F")
M = cp.intvar(1, 5, name="M")
S = cp.intvar(1, 5, name="S")

# Constraints
model += cp.AllDifferent([B, C, F, M, S])  # all live on different floors
model += (B != 5)                          # Baker not on 5th
model += (C != 1)                          # Cooper not on 1st
model += (F != 1) & (F != 5)               # Fletcher not on 1st or 5th
model += (M > C)                           # Miller above Cooper
model += (cp.Abs(S - F) >= 2)              # Smith not adjacent to Fletcher
model += (cp.Abs(F - C) >= 2)              # Fletcher not adjacent to Cooper

# Solve and print
if model.solve():
    solution = {
        'B': int(B.value()),
        'C': int(C.value()),
        'F': int(F.value()),
        'M': int(M.value()),
        'S': int(S.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
