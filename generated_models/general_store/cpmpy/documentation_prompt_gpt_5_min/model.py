
import cpmpy as cp
import json

# Letters: C, H, E, S, A, B, O, W, P, L
letters = list("CHESABOWPL")  # Note: order chosen to match required output keys (C,H,E,S,A,B,O,W,P,L)

# Words to sum (each word is right-aligned under the 7-letter total ALLWOOL)
words = [
    "CHESS",
    "CASH",
    "BOWWOW",
    "CHOPS",
    "ALSOPS",
    "PALEALE",
    "COOL",
    "BASS",
    "HOPS",
    "ALES",
    "HOES",
    "APPLES",
    "COWS",
    "CHEESE",
    "CHSOAP",
    "SHEEP"
]

# Result word ALLWOOL (length 7)
result_word = "ALLWOOL"
ncols = len(result_word)  # 7 columns

# Create model
model = cp.Model()

# Decision variables for letters
L = {ch: cp.intvar(0, 9, name=ch) for ch in letters}

# All letters different
model += cp.AllDifferent([L[ch] for ch in letters])

# Leading letters that cannot be zero:
# Leading letters of addends and of the result (first letter of each word and result)
leading_letters = set()
for w in words:
    leading_letters.add(w[0])
leading_letters.add(result_word[0])
# Enforce non-zero for these (they are among our letters)
for ch in leading_letters:
    # Some letters might not be in our variable set (but in this puzzle they are)
    if ch in L:
        model += (L[ch] >= 1)

# Prepare column contributions: for each column (0..6 left->right), sum letter values of words aligned to right
# Right-align each word under the 7-letter result
cols = [[] for _ in range(ncols)]
for w in words:
    offset = ncols - len(w)  # starting column index for this word
    for i, ch in enumerate(w):
        col = offset + i
        # add the variable corresponding to ch to that column
        cols[col].append(L[ch])

# Convert each column list to a sum expression (empty positions contribute 0)
col_sums = [cp.sum(col) if len(col) > 0 else 0 for col in cols]

# Result digits per column (A L L W O O L)
result_digits = [L[ch] for ch in result_word]

# Carry variables c[0..7] where c[7] is carry into rightmost column (set to 0),
# and constraint: for each column j (0..6 left->right):
#   col_sums[j] + c[j+1] == result_digits[j] + 10*c[j]
c = cp.intvar(0, 20, shape=8, name="c")  # upper bound 20 is safe for these sums
# carry into rightmost column is c[7] and must be 0
model += (c[7] == 0)
# also no overflow beyond leftmost: c[0] == 0
model += (c[0] == 0)

for j in range(ncols):
    model += (col_sums[j] + c[j+1] == result_digits[j] + 10 * c[j])

# Solve
if model.solve():
    solution = {
        'C': int(L['C'].value()),
        'H': int(L['H'].value()),
        'E': int(L['E'].value()),
        'S': int(L['S'].value()),
        'A': int(L['A'].value()),
        'B': int(L['B'].value()),
        'O': int(L['O'].value()),
        'W': int(L['W'].value()),
        'P': int(L['P'].value()),
        'L': int(L['L'].value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
