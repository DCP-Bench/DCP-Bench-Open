
import cpmpy as cp
import json
import numpy as np

# Word list sorted by descending length then alphabetically
words = ["HOSES", "LASER", "SAILS", "SHEET", "STEER",   # length 5, indices 0..4
         "HEEL", "HIKE", "KEEL", "KNOT", "LINE",       # length 4, indices 5..9
         "AFT", "ALE", "EEL", "LEE", "TIE"]            # length 3, indices 10..14

# Precompute letter codes (A=0,...,Z=25), pad to length 5 with -1
maxlen = 5
LET = []
for w in words:
    codes = [ord(c) - ord('A') for c in w]
    # pad shorter words with -1 (unused)
    codes += [-1] * (maxlen - len(codes))
    LET.append(codes)
LET = np.array(LET, dtype=int)

# Model definition
model = cp.Model()

# Decision variables: pos1..pos8
# Domains according to word lengths required at each position:
# pos1, pos2, pos3, pos8 need length 5 -> indices 0..4
# pos4, pos5 need length 4 -> indices 5..9
# pos6, pos7 need length 3 -> indices 10..14
pos1 = cp.IntVar(0, 4, name="pos1")
pos2 = cp.IntVar(0, 4, name="pos2")
pos3 = cp.IntVar(0, 4, name="pos3")
pos8 = cp.IntVar(0, 4, name="pos8")
pos4 = cp.IntVar(5, 9, name="pos4")
pos5 = cp.IntVar(5, 9, name="pos5")
pos6 = cp.IntVar(10, 14, name="pos6")
pos7 = cp.IntVar(10, 14, name="pos7")

# All selected words must be different
model += cp.AllDifferent([pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8])

# Helper for element constraints
# cp.element(array, var_index, fixed_index) -> array[var_index, fixed_index]
el = cp.element

# Intersection constraints:
# pos1[2] == pos2[0]  at (1,3)
model += el(LET, pos1, 2) == el(LET, pos2, 0)
# pos1[4] == pos3[0]  at (1,5)
model += el(LET, pos1, 4) == el(LET, pos3, 0)
# pos2[2] == pos4[1]  at (3,3)
model += el(LET, pos2, 2) == el(LET, pos4, 1)
# pos3[2] == pos4[3]  at (3,5)
model += el(LET, pos3, 2) == el(LET, pos4, 3)
# pos4[2] == pos5[0]  at (3,4)
model += el(LET, pos4, 2) == el(LET, pos5, 0)
# pos2[3] == pos7[0]  at (4,3)
model += el(LET, pos2, 3) == el(LET, pos7, 0)
# pos5[1] == pos7[1]  at (4,4)
model += el(LET, pos5, 1) == el(LET, pos7, 1)
# pos3[3] == pos7[2]  at (4,5)
model += el(LET, pos3, 3) == el(LET, pos7, 2)
# pos6[1] == pos8[0]  at (5,1)
model += el(LET, pos6, 1) == el(LET, pos8, 0)
# pos2[4] == pos8[2]  at (5,3)
model += el(LET, pos2, 4) == el(LET, pos8, 2)
# pos5[2] == pos8[3]  at (5,4)
model += el(LET, pos5, 2) == el(LET, pos8, 3)
# pos3[4] == pos8[4]  at (5,5)
model += el(LET, pos3, 4) == el(LET, pos8, 4)

# Solve and print
if model.solve():
    E = [int(pos1.value()), int(pos2.value()), int(pos3.value()),
         int(pos4.value()), int(pos5.value()), int(pos6.value()),
         int(pos7.value()), int(pos8.value())]
    solution = {'E': E}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
