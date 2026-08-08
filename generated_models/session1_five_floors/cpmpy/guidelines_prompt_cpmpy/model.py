
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
B = cp.IntVar(1, 5, name="B")  # Baker
C = cp.IntVar(1, 5, name="C")  # Cooper
F = cp.IntVar(1, 5, name="F")  # Fletcher
M = cp.IntVar(1, 5, name="M")  # Miller
S = cp.IntVar(1, 5, name="S")  # Smith

# Constraints
model += cp.AllDifferent([B, C, F, M, S])
model += (B != 5)          # Baker does not live on the fifth floor
model += (C != 1)          # Cooper does not live on the first floor
model += (F != 1)          # Fletcher does not live on the first floor
model += (F != 5)          # Fletcher does not live on the fifth floor
model += (M > C)           # Miller lives on a higher floor than Cooper
model += (cp.abs(S - F) != 1)  # Smith does not live adjacent to Fletcher
model += (cp.abs(F - C) != 1)  # Fletcher does not live adjacent to Cooper

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
