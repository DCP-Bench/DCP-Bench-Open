from cpmpy import *
import json

# Decision Variables
letters = "ABCDEFGHIJKLMNOPRSTUVWXY"  # All letters except Q and Z, in alphabetical order
dice = intvar(0, 3, shape=len(letters), name="dice")  # dice[letter_idx] = block_num

# Model
model = Model()

# Words that can be spelled
words = ["BAKE", "ONYX", "ECHO", "OVAL", "GIRD", "SMUG", "JUMP", "TORN", "LUCK", "VINY", "LUSH", "WRAP"]

# Constraint: For each word, all letters must be on different blocks
for word in words:
    letter_indices = [letters.index(c) for c in word]
    model += AllDifferent([dice[i] for i in letter_indices])

# Constraint: Each block must have exactly 6 letters
for block in range(4):
    model += sum(dice == block) == 6

# Solve
model.solve()

# Print solution
solution = {"dice": dice.value().tolist()}
print(json.dumps(solution))