
import cpmpy as cp
import json

# Data
# Words sorted by length (descending) then alphabetically:
# indices: 0..14
words = [
    "HOSES",  # 0
    "LASER",  # 1
    "SAILS",  # 2
    "SHEET",  # 3
    "STEER",  # 4
    "HEEL",   # 5
    "HIKE",   # 6
    "KEEL",   # 7
    "KNOT",   # 8
    "LINE",   # 9
    "AFT",    # 10
    "ALE",    # 11
    "EEL",    # 12
    "LEE",    # 13
    "TIE"     # 14
]

# Precompute letter codes (A->0,...,Z->25)
word_codes = [ [ord(c)-ord('A') for c in w] for w in words ]
word_lengths = [ len(w) for w in words ]

# Slots definition (numbered 1..8 in puzzle), 0-based indices in code:
# Each slot is (list_of_coords) where coords are (row, col) 1-based for readability, but any identity ok
# We define according to deduced directions/lengths:
# 1: (1,1)-(1,5) across, length 5
# 2: (1,3)-(5,3) down, length 5
# 3: (1,5)-(5,5) down, length 5
# 4: (3,2)-(3,5) across, length 4
# 5: (3,4)-(6,4) down, length 4
# 6: (4,1)-(6,1) down, length 3
# 7: (4,3)-(4,5) across, length 3
# 8: (5,1)-(5,5) across, length 5

slots = [
    [(1,1),(1,2),(1,3),(1,4),(1,5)],             # slot 1, len=5
    [(1,3),(2,3),(3,3),(4,3),(5,3)],             # slot 2, len=5
    [(1,5),(2,5),(3,5),(4,5),(5,5)],             # slot 3, len=5
    [(3,2),(3,3),(3,4),(3,5)],                   # slot 4, len=4
    [(3,4),(4,4),(5,4),(6,4)],                   # slot 5, len=4
    [(4,1),(5,1),(6,1)],                         # slot 6, len=3
    [(4,3),(4,4),(4,5)],                         # slot 7, len=3
    [(5,1),(5,2),(5,3),(5,4),(5,5)]              # slot 8, len=5
]

slot_lengths = [len(s) for s in slots]

# Allowed word indices per slot by required length
len5_indices = [i for i,l in enumerate(word_lengths) if l == 5]  # [0..4]
len4_indices = [i for i,l in enumerate(word_lengths) if l == 4]  # [5..9]
len3_indices = [i for i,l in enumerate(word_lengths) if l == 3]  # [10..14]

allowed_per_slot = []
for L in slot_lengths:
    if L == 5:
        allowed_per_slot.append(len5_indices)
    elif L == 4:
        allowed_per_slot.append(len4_indices)
    elif L == 3:
        allowed_per_slot.append(len3_indices)
    else:
        allowed_per_slot.append([])  # should not happen

# Model definition
model = cp.Model()

# Decision Variables
# E[s]: chosen word index (0..14) for slot s (s=0..7), these must be all different
E = cp.intvar(0, 14, shape=len(slots), name="E")

# I[s]: index within allowed list for slot s (0..len(allowed)-1)
I = [cp.intvar(0, len(allowed_per_slot[s])-1, name=f"I_{s}") for s in range(len(slots))]

# Letters per slot position: char_vars[s][p] in 0..25
char_vars = [cp.intvar(0,25, shape=len(slots[s]), name=f"C_{s}") for s in range(len(slots))]

# Constraints

# Map I[s] through allowed list to E[s]
for s in range(len(slots)):
    allowed = allowed_per_slot[s]
    # E[s] == allowed[I[s]]
    model += (E[s] == cp.Element(allowed, I[s]))
    # Link letters per position using the chosen I[s]
    for p in range(len(slots[s])):
        # Build table of letter codes at position p for allowed words
        letter_table = [word_codes[idx][p] for idx in allowed]
        model += (char_vars[s][p] == cp.Element(letter_table, I[s]))

# All words must be different
model += cp.AllDifferent(E)

# Intersection constraints: equal letters on overlapping coordinates
# Build a mapping from coordinate to list of (slot_index, position_index)
coord_map = {}
for s, coords in enumerate(slots):
    for p, rc in enumerate(coords):
        coord_map.setdefault(rc, []).append((s, p))

# For any coordinate with multiple occupants, enforce equality of letters
for rc, lst in coord_map.items():
    if len(lst) >= 2:
        # enforce all equal
        first_s, first_p = lst[0]
        for (s, p) in lst[1:]:
            model += (char_vars[first_s][first_p] == char_vars[s][p])

# Objective (none)

# Solve and print
if model.solve():
    solution = {'E': E.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
