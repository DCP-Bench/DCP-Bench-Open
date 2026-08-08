
import cpmpy as cp
import json

# Letters: all except Q and Z, in alphabetical order
letters = [chr(i) for i in range(ord('A'), ord('Z')+1) if chr(i) not in ('Q', 'Z')]
# words to be spelled (given)
words = ["BAKE", "ONYX", "ECHO", "OVAL",
         "GIRD", "SMUG", "JUMP", "TORN",
         "LUCK", "VINY", "LUSH", "WRAP"]

# Model definition
model = cp.Model()

# Decision Variables: which of the 4 dice (0..3) each letter is on
dice = cp.intvar(0, 3, shape=len(letters), name="dice")

# Helper: map letter to index in 'letters' list
idx = {letters[i]: i for i in range(len(letters))}

# Constraints
# Each die must have exactly 6 letters (4 dice * 6 faces = 24 letters)
for d in range(4):
    model += (cp.Count(dice, d) == 6)

# For each word, the letters must be on distinct dice (can't reuse a block)
for w in words:
    model += cp.AllDifferent([dice[idx[ch]] for ch in w])

# Solve and print
if model.solve():
    solution = {'dice': dice.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
