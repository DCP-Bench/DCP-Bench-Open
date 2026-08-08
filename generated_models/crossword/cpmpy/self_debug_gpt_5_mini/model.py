
import cpmpy as cp
import json
import numpy as np

# Words sorted by length (desc) then alphabetically as specified:
# 5-letter: HOSES, LASER, SAILS, SHEET, STEER
# 4-letter: HEEL, HIKE, KEEL, KNOT, LINE
# 3-letter: AFT, ALE, EEL, LEE, TIE
words = [
    "HOSES","LASER","SAILS","SHEET","STEER",
    "HEEL","HIKE","KEEL","KNOT","LINE",
    "AFT","ALE","EEL","LEE","TIE"
]

# map letters to integers A=1..Z=26
def word_to_nums(w, maxlen=5):
    nums = [ord(ch) - ord('A') + 1 for ch in w]
    # pad with 0s (won't be used for positions beyond word length)
    nums += [0] * (maxlen - len(nums))
    return nums

maxlen = 5
words_nums = np.array([word_to_nums(w, maxlen) for w in words], dtype=int)

# Grid definition 6 rows x 5 cols
# True = non-black (letter), False = black
grid_nonblack = [[True]*5 for _ in range(6)]
black_cells = [(2,1),(2,2),(2,4),(3,1),(4,2),(6,2),(6,3),(6,5)]
# convert to 0-based indexing and mark black
for (r,c) in black_cells:
    grid_nonblack[r-1][c-1] = False

# Helper to create slot cell lists (0-based coords)
def cells_across(r,c):
    cells = []
    cc = c
    while cc < 5 and grid_nonblack[r][cc]:
        cells.append((r,cc))
        cc += 1
    return cells

def cells_down(r,c):
    cells = []
    rr = r
    while rr < 6 and grid_nonblack[rr][c]:
        cells.append((rr,c))
        rr += 1
    return cells

# Slot definitions for two cases (case A: slot2 across len3; case B: slot2 down len5)
# We'll try both cases and stop at first feasible solution.

# Fixed slots (positions are 0-based)
slot_positions_fixed = {
    1: ("across", (0,0)),   # number 1 at (1,1)
    3: ("down",   (0,4)),   # number 3 at (1,5)
    4: ("across", (2,1)),   # number 4 at (3,2)
    5: ("down",   (2,3)),   # number 5 at (3,4)
    6: ("down",   (3,0)),   # number 6 at (4,1)
    7: ("across", (3,2)),   # number 7 at (4,3)
    8: ("across", (4,0)),   # number 8 at (5,1)
}
# slot 2 handled separately per case

# Precompute allowed word indices by length
len_to_indices = {
    5: [i for i,w in enumerate(words) if len(w)==5],
    4: [i for i,w in enumerate(words) if len(w)==4],
    3: [i for i,w in enumerate(words) if len(w)==3]
}

def build_and_solve(case_name):
    model = cp.Model()
    # slots 1..8
    slot_cells = {}
    slot_lengths = {}
    # fill fixed slots
    for s, (orient, (r0,c0)) in slot_positions_fixed.items():
        if orient == "across":
            cells = cells_across(r0,c0)
        else:
            cells = cells_down(r0,c0)
        slot_cells[s] = cells
        slot_lengths[s] = len(cells)
    # slot 2 per case
    if case_name == "A":  # slot2 across (length 3)
        s2_orient = "across"
    else:                # case B: slot2 down (length 5)
        s2_orient = "down"
    s = 2
    r0,c0 = (0,2)  # (1,3) in 1-based -> (0,2)
    if s2_orient == "across":
        cells = cells_across(r0,c0)
    else:
        cells = cells_down(r0,c0)
    slot_cells[2] = cells
    slot_lengths[2] = len(cells)

    # Create word index variables for each slot (0..14) but constrained to allowed lengths
    slot_word_idx = {}
    for s in range(1,9):
        widx = cp.intvar(0, len(words)-1, name=f"w{s}")
        model += cp.InDomain(widx, len_to_indices[slot_lengths[s]])
        slot_word_idx[s] = widx

    # Letter variables for each slot position
    slot_letters = {}
    for s in range(1,9):
        L = slot_lengths[s]
        # letter domain 1..26
        slot_letters[s] = [cp.intvar(1,26, name=f"l{s}_{p}") for p in range(L)]
        # link each slot letter p to corresponding column in words_nums via Element
        for p in range(L):
            # Element over words_nums[:,p] with index slot_word_idx[s]
            model += cp.Element(words_nums[:,p].tolist(), slot_word_idx[s]) == slot_letters[s][p]

    # Cell-wise equality: if multiple slot-letter variables map to same grid cell, equate them
    cell_to_letters = {}
    for s in range(1,9):
        cells = slot_cells[s]
        for p,cell in enumerate(cells):
            cell_to_letters.setdefault(cell, []).append(slot_letters[s][p])
    # Enforce equality among entries for each cell (if cell used by >1 slot)
    for cell, lvars in cell_to_letters.items():
        for i in range(1, len(lvars)):
            model += (lvars[0] == lvars[i])

    # All chosen words must be distinct
    model += cp.AllDifferent([slot_word_idx[s] for s in range(1,9)])

    # Solve
    if model.solve():
        E = [int(slot_word_idx[s].value()) for s in range(1,9)]
        return E
    else:
        return None

solution = build_and_solve("A")
if solution is None:
    solution = build_and_solve("B")

if solution is not None:
    # Print as requested: E list of 8 integers
    solution_dict = {'E': solution}
    print(json.dumps(solution_dict, indent=4))
else:
    print("No solution found.")
