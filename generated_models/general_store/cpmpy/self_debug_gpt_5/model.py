
import cpmpy as cp
import json

# Data: define all addend words and the result word
addends = [
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

# All distinct letters involved (given explicitly in the problem)
letters_list = ['C', 'H', 'E', 'S', 'A', 'B', 'O', 'W', 'P', 'L']

# Model definition
model = cp.Model()

# Decision Variables: each letter is a digit 0..9, all different
letter_vars = {ch: cp.intvar(0, 9, name=ch) for ch in letters_list}
model += cp.AllDifferent(list(letter_vars.values()))

# Leading letters must be non-zero (for each addend and the result)
leading_letters = set([w[0] for w in addends] + [result_word[0]])
for ch in leading_letters:
    model += (letter_vars[ch] != 0)

# Column-wise addition constraints with carry
# result has 7 digits, create carry variables c[0..7], with c[0]=0 and c[7]=0
num_cols = len(result_word)  # 7
carry = cp.intvar(0, 20, shape=num_cols + 1, name="carry")
# Initial and final carry constraints
model += (carry[0] == 0)
model += (carry[num_cols] == 0)

# Helper to get the k-th (from right) letter of a word, or None if shorter
def kth_from_right(word, k):
    # k=0 is units position
    if k < len(word):
        return word[len(word) - 1 - k]
    else:
        return None

# Map result digits per column from rightmost to leftmost
result_digits = [result_word[len(result_word) - 1 - k] for k in range(num_cols)]

for k in range(num_cols):
    # Collect all letters that contribute to column k (from right)
    col_letters = []
    for w in addends:
        ch = kth_from_right(w, k)
        if ch is not None:
            col_letters.append(letter_vars[ch])
    # Sum constraint: sum(column letters) + carry_in = result_digit + 10*carry_out
    # Use cp.sum for CPMpy
    col_sum = cp.sum(col_letters) if len(col_letters) > 0 else 0
    model += (col_sum + carry[k] == letter_vars[result_digits[k]] + 10 * carry[k + 1])

# Solve and print
if model.solve():
    solution = {
        'C': int(letter_vars['C'].value()),
        'H': int(letter_vars['H'].value()),
        'E': int(letter_vars['E'].value()),
        'S': int(letter_vars['S'].value()),
        'A': int(letter_vars['A'].value()),
        'B': int(letter_vars['B'].value()),
        'O': int(letter_vars['O'].value()),
        'W': int(letter_vars['W'].value()),
        'P': int(letter_vars['P'].value()),
        'L': int(letter_vars['L'].value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
