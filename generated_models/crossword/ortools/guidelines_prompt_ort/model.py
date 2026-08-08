
from ortools.sat.python import cp_model
import json

# List of words sorted by length (descending) and then alphabetically
words = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",   # length 5 (indices 0-4)
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",        # length 4 (indices 5-9)
    "AFT", "ALE", "EEL", "LEE", "TIE"              # length 3 (indices 10-14)
]

# Precompute integer codes for letters (A=0, B=1, ..., Z=25)
letter_ints = [[ord(ch) - ord('A') for ch in w] for w in words]

# Crossword word slots: (orientation, start_row, start_col, length)
# orientation: 'A' for across, 'D' for down
slots = [
    ('A', 1, 1, 5),  # word 1
    ('D', 1, 3, 5),  # word 2
    ('D', 1, 5, 5),  # word 3
    ('A', 3, 2, 4),  # word 4
    ('D', 3, 4, 4),  # word 5
    ('D', 4, 1, 3),  # word 6
    ('A', 4, 3, 3),  # word 7
    ('A', 5, 1, 5),  # word 8
]

model = cp_model.CpModel()

# Define index domains by word length
len5 = [0, 1, 2, 3, 4]
len4 = [5, 6, 7, 8, 9]
len3 = [10, 11, 12, 13, 14]
length_domains = {5: len5, 4: len4, 3: len3}

# Decision variables: E[i] is the index (0..14) of the chosen word for slot i
E = []
for i, slot in enumerate(slots):
    _, _, _, length = slot
    dom = length_domains[length]
    var = model.NewIntVarFromDomain(cp_model.Domain.FromValues(dom), f"E{i}")
    E.append(var)

# Letter variables: L[i][j] is the letter code at position j of slot i
L = []
max_len = max(s[3] for s in slots)
for i, slot in enumerate(slots):
    _, _, _, length = slot
    row = []
    for j in range(length):
        lv = model.NewIntVar(0, 25, f"L{i}_{j}")
        # Build a table of length-15 for the j-th letter of each word (dummy 0 if too short)
        table_j = [
            letter_ints[k][j] if j < len(letter_ints[k]) else 0
            for k in range(len(words))
        ]
        model.AddElement(E[i], table_j, lv)
        row.append(lv)
    L.append(row)

# Intersection constraints: cells where two slots cross must have equal letters
# Map each slot to its covered cells
cell_map = {}  # (r,c) -> list of (slot_index, position_in_slot)
for i, slot in enumerate(slots):
    orient, r, c, length = slot
    for j in range(length):
        rr = r + (j if orient == 'D' else 0)
        cc = c + (j if orient == 'A' else 0)
        cell_map.setdefault((rr, cc), []).append((i, j))

# Enforce that at each cell, all letters from all covering slots agree
for cell, entries in cell_map.items():
    if len(entries) > 1:
        # pick the first and equate all others to it
        base_i, base_j = entries[0]
        for other_i, other_j in entries[1:]:
            model.Add(L[base_i][base_j] == L[other_i][other_j])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution as JSON
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'E': [solver.Value(E[i]) for i in range(len(E))]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
