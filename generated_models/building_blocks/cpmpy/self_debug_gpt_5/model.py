
import cpmpy as cp
import json
import string

# Data
# Letters: all A..Z except Q and Z (total 24 letters)
letters = [ch for ch in string.ascii_uppercase if ch not in ('Q', 'Z')]
letter_index = {ch: i for i, ch in enumerate(letters)}

# Words that must be spellable (each letter from a different block)
words = [
    "BAKE", "ONYX", "ECHO", "OVAL",
    "GIRD", "SMUG", "JUMP", "TORN",
    "LUCK", "VINY", "LUSH", "WRAP"
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# dice[i] = block index (0..3) for letter letters[i]
dice = cp.intvar(0, 3, shape=len(letters), name="dice")

# Constraints

# 1) Each block must contain exactly 6 letters
for b in range(4):
    model += (cp.Count(dice, b) == 6)

# 2) For each word, its four letters must be on four distinct blocks
for w in words:
    indices = [letter_index[ch] for ch in w]
    model += cp.AllDifferent([dice[i] for i in indices])

# Objective (none)

# Solve and print
if model.solve():
    solution = {'dice': dice.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
