
import cpmpy as cp
import json

# Variables with their domains based on constraints
B = cp.intvar(1, 4, name="B")  # Baker cannot be on 5th floor
C = cp.intvar(2, 5, name="C")  # Cooper cannot be on 1st floor
F = cp.intvar(2, 4, name="F")  # Fletcher cannot be on 1st or 5th floor
M = cp.intvar(1, 5, name="M")  # Miller's floor (constrained by M > C)
S = cp.intvar(1, 5, name="S")  # Smith's floor

model = cp.Model()

# All different floors constraint
model += cp.AllDifferent([B, C, F, M, S])

# Miller lives higher than Cooper
model += (M > C)

# Smith not adjacent to Fletcher
model += (cp.abs(S - F) != 1)

# Fletcher not adjacent to Cooper
model += (cp.abs(F - C) != 1)

# Solve and print solution
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
