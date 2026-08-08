
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: floors for each person (1 to 5)
B = cp.intvar(1, 5, name="B")
C = cp.intvar(1, 5, name="C")
F = cp.intvar(1, 5, name="F")
M = cp.intvar(1, 5, name="M")
S = cp.intvar(1, 5, name="S")

# Constraints
model += (B != 5)  # Baker does not live on the fifth floor
model += (C != 1)  # Cooper does not live on the first floor
model += (F != 1) & (F != 5)  # Fletcher does not live on the first or fifth floor
model += (M > C)  # Miller lives on a higher floor than Cooper
model += (cp.abs(S - F) > 1)  # Smith does not live adjacent to Fletcher
model += (cp.abs(F - C) > 1)  # Fletcher does not live adjacent to Cooper
model += cp.AllDifferent([B, C, F, M, S])  # All live on different floors

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
