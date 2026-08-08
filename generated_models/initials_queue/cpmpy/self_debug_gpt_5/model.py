
import cpmpy as cp
import json
import numpy as np

# Data
# Map letters A..E to 0..4 and list all alphabetically ordered distinct pairs
pairs = [
    (0,1),  # AB
    (0,2),  # AC
    (0,3),  # AD
    (0,4),  # AE
    (1,2),  # BC
    (1,3),  # BD
    (1,4),  # BE
    (2,3),  # CD
    (2,4),  # CE
    (3,4)   # DE
]
pairs = np.array(pairs, dtype=int)

# Precompute allowed transitions: adjacent pairs must share no letter
allowed = []
for i in range(len(pairs)):
    for j in range(len(pairs)):
        a1, a2 = pairs[i]
        b1, b2 = pairs[j]
        if (a1 != b1) and (a1 != b2) and (a2 != b1) and (a2 != b2):
            allowed.append([i, j])

# Indices of fixed positions
idx_AB = 0
idx_AC = 1
idx_AD = 2
idx_AE = 3
idx_BC = 4
idx_BD = 5
idx_BE = 6
idx_CD = 7
idx_CE = 8
idx_DE = 9

# Model definition
model = cp.Model()

# Decision Variables
q = cp.intvar(0, 9, shape=10, name="q")  # permutation of the 10 pairs

# Constraints
# All different: each pair used exactly once
model += cp.AllDifferent(q)

# Fixed positions: BE at front, CD second, BD at end
model += (q[0] == idx_BE)
model += (q[1] == idx_CD)
model += (q[9] == idx_BD)

# Adjacency constraints: no shared letters between consecutive people
for i in range(9):
    model += cp.Table([q[i], q[i+1]], allowed)

# Solve and print
if model.solve():
    q_vals = q.value().tolist()
    queue = [pairs[idx].tolist() for idx in q_vals]
    solution = {'queue': queue}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
