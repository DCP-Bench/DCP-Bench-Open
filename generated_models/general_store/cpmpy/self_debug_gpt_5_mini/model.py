
import cpmpy as cp
import json

# Data
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
# Letters present in the puzzle (explicit order requested in print statement)
letters = list("CHESABOWPL")  # C, H, E, S, A, B, O, W, P, L

# Model
model = cp.Model()

# Decision Variables: digits for each letter
L = {ch: cp.intvar(0, 9, name=ch) for ch in letters}

# All letters different
model += cp.AllDifferent([L[ch] for ch in letters])

# Leading letters cannot be zero (first letter of each addend and result)
leading_letters = set(w[0] for w in words)
leading_letters.add(result_word[0])
for ch in leading_letters:
    if ch in L:
        model += (L[ch] >= 1)

# Helper: compute integer value of a word (most significant digit at index 0)
def word_value(word):
    n = len(word)
    # place value: 10^(n-1-i) for i-th char
    terms = []
    for i, ch in enumerate(word):
        power = 10 ** (n - 1 - i)
        terms.append(L[ch] * power)
    return cp.sum(terms)

# Compute integer values for all addends and the result
addend_values = [word_value(w) for w in words]
result_value = word_value(result_word)

# Sum of addends equals result
model += (cp.sum(addend_values) == result_value)

# Solve and print
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
