
import cpmpy as cp
import json

# Define the 9x9 grid variables: 0 for blocks or digit 0-9 for white cells
M = cp.intvar(0, 9, shape=(9, 9), name="M")

# Helper to convert 1-based positions to 0-based
def pos(r, c):
    return (r - 1, c - 1)

# List of block positions (row, col) 1-based from the diagram
blocks = [
    (1,5), (2,3), (2,7), (3,2), (3,5), (3,8),
    (4,5), (5,1), (5,3), (5,4), (5,5), (5,6), (5,7), (5,9),
    (6,5), (7,2), (7,5), (7,8),
    (8,3), (8,7),
    (9,5)
]

# Across clue start positions and their lengths
across_slots = {
    1:  [(1,1),(1,2),(1,3),(1,4)],
    4:  [(1,6),(1,7),(1,8),(1,9)],
    7:  [(2,1),(2,2)],
    8:  [(2,4),(2,5),(2,6)],
    9:  [(2,8),(2,9)],
    10: [(3,3),(3,4)],
    11: [(3,6),(3,7)],
    13: [(4,1),(4,2),(4,3),(4,4)],
    15: [(4,6),(4,7),(4,8),(4,9)],
    17: [(6,1),(6,2),(6,3),(6,4)],
    20: [(6,6),(6,7),(6,8),(6,9)],
    23: [(7,3),(7,4)],
    24: [(7,6),(7,7)],
    25: [(8,1),(8,2)],
    27: [(8,4),(8,5),(8,6)],
    28: [(8,8),(8,9)],
    29: [(9,1),(9,2),(9,3),(9,4)],
    30: [(9,6),(9,7),(9,8),(9,9)]
}

# Down clue start positions and their lengths
down_slots = {
    1:  [(1,1),(2,1),(3,1),(4,1)],
    2:  [(1,2),(2,2)],
    3:  [(1,4),(2,4),(3,4),(4,4)],
    4:  [(1,6),(2,6),(3,6),(4,6)],
    5:  [(1,8),(2,8)],
    6:  [(1,9),(2,9),(3,9),(4,9)],
    10: [(3,3),(4,3)],
    12: [(3,7),(4,7)],
    14: [(4,2),(5,2),(6,2)],
    16: [(4,8),(5,8),(6,8)],
    17: [(6,1),(7,1),(8,1),(9,1)],
    18: [(6,3),(7,3)],
    19: [(6,4),(7,4),(8,4),(9,4)],
    20: [(6,6),(7,6),(8,6),(9,6)],
    21: [(6,7),(7,7)],
    22: [(6,9),(7,9),(8,9),(9,9)],
    26: [(8,2),(9,2)],
    28: [(8,8),(9,8)]
}

# Create model
model = cp.Model()

# 1) Enforce blocks to be zero
for (r, c) in blocks:
    model += (M[pos(r, c)] == 0)

# 2) Create integer variables for each clue
# Across and down variables
A = {n: cp.intvar(0, 9999, name=f"A{n}") for n in across_slots}
D = {n: cp.intvar(0, 9999, name=f"D{n}") for n in down_slots}

# 3) Link slot variables to the digit cells M
def link_number(var, cells):
    """var == concatenation of M at cells (list of (r,c)), first digit >0."""
    L = len(cells)
    coeffs = [10**(L-1-i) for i in range(L)]
    # sum of digits * place
    model += (var == cp.sum([M[pos(r, c)] * coeffs[i] for i, (r, c) in enumerate(cells)]))
    # no leading zero
    r0, c0 = cells[0]
    model += (M[pos(r0, c0)] >= 1)

for n, cells in across_slots.items():
    link_number(A[n], cells)
for n, cells in down_slots.items():
    link_number(D[n], cells)

# 4) Clue constraints
# Across clues
model += (A[1]  == 2 * A[27])
model += (A[4]  == D[4] + 71)
model += (A[7]  == D[18] + 4)
model += (D[6]  == A[8] * 16)   # A[8] == D[6] / 16
model += (A[9]  == D[2] - 18)
model += (A[10] == 72)
model += (A[11] == D[5] - 70)
model += (A[13] == D[26] * A[23])
model += (A[15] == D[6] - 350)
model += (A[17] == A[25] * A[23])
# A20 is a 4-digit square number
t = cp.intvar(32, 99, name="t20")
model += (A[20] == t * t)
# A23 is prime (2-digit)
primes2 = [p for p in range(10, 100)
           if p > 1 and all(p % d for d in range(2, int(p**0.5)+1))]
model += sum([A[23] == p for p in primes2]) == 1
# A24 is a 2-digit square
squares2 = [16, 25, 36, 49, 64, 81]
model += sum([A[24] == s for s in squares2]) == 1
model += (A[25] == A[20] // 17)  # divisible by 17
model += (A[28] == 48)
model += (A[29] == 7 * 144)  # 1008
model += (A[27] * 4 == D[6]) # A27 == D6 / 4
model += (A[30] == D[22] + 450)

# Down clues
model += (D[1]   == A[1] + 27)
model += (D[2]   == 5 * 12)     # 60
model += (D[3]   == A[30] + 888)
model += (D[4]   == 2 * A[17])
model += (D[5]   == A[29] // 12)  # 84
model += (D[6]   == A[28] * A[23])
model += (D[10]  == A[10] + 4)    # 76
model += (D[12]  == 3 * A[24])
model += (D[14]  == A[13] // 16)
model += (D[16]  == D[28] * 15)
model += (D[17]  == A[13] - 399)
model += (D[18]  == A[29] // 18)  # 56
model += (D[19]  == D[22] - 94)
model += (D[20]  == A[20] - 9)
model += (D[21]  == A[25] - 52)
model += (D[22]  == D[20] * 6)
model += (D[26]  == 5 * A[24])
model += (D[28]  == D[21] + 27)

# 5) Solve and print
if model.solve():
    M_val = M.value().tolist()
    # ensure blocks are represented as 0
    print(json.dumps({"M": M_val}, indent=4))
else:
    print("No solution found.")
