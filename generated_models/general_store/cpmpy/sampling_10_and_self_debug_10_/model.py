
import cpmpy as cp
import json

# Data: words (right-aligned under result "ALLWOOL")
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

result_word = "ALLWOOL"
ncols = len(result_word)  # 7

# Collect all unique letters used
unique_letters = sorted({ch for w in words for ch in w} | set(result_word))
# The problem statement asks to print values for (C, H, E, S, A, B, O, W, P, L)
# Ensure that exactly these letters are present and in that order for printing
required_print_order = ['C','H','E','S','A','B','O','W','P','L']
# Create decision variables for these letters (and any others if present)
letters = required_print_order[:]  # main letters
# Ensure all unique letters are included in variables
for ch in unique_letters:
    if ch not in letters:
        letters.append(ch)

# Model
model = cp.Model()

# Letter variables: each letter is a digit 0..9
L = {ch: cp.intvar(0, 9, name=ch) for ch in letters}

# All different for the letters that actually represent digits
model += cp.AllDifferent([L[ch] for ch in letters])

# Leading letters (most significant letter of each addend and of the result) cannot be zero
leading_letters = set(w[0] for w in words)
leading_letters.add(result_word[0])
for ch in leading_letters:
    if ch in L:
        model += (L[ch] >= 1)

# Build columns right-to-left (index 0 is rightmost / units column)
cols = [[] for _ in range(ncols)]
for w in words:
    # right-align: last character of w goes to cols[0], second-last to cols[1], etc.
    for i, ch in enumerate(reversed(w)):
        cols[i].append(L[ch])

# Result digits right-to-left (result_word last char at index 0)
result_digits = [L[ch] for ch in reversed(result_word)]

# Carry variables: c[k] is carry into column k (k=0 is into rightmost). c has length ncols+1.
# We require c[0] == 0 (no carry into rightmost) and c[ncols] == 0 (no overflow beyond leftmost)
c = cp.intvar(0, 50, shape=ncols + 1, name="c")
model += (c[0] == 0)
model += (c[ncols] == 0)

# Column constraints (right-to-left):
# For column k: sum(cols[k]) + c[k] == result_digits[k] + 10 * c[k+1]
for k in range(ncols):
    col_sum = cp.sum(cols[k]) if len(cols[k]) > 0 else 0
    model += (col_sum + c[k] == result_digits[k] + 10 * c[k+1])

# Solve
if model.solve():
    # Prepare solution dict with required keys in exact order/names
    solution = {ch: int(L[ch].value()) for ch in required_print_order}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
