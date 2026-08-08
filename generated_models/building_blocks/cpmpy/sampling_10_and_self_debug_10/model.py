
import cpmpy as cp
import json

# The problem:
# We have 4 blocks, each with 6 letters on its sides.
# The 4 blocks collectively contain every letter except Q and Z.
# By arranging the blocks in various ways (choosing which side of each block is visible),
# we can spell all given words.
# We want to find which block contains each letter. The output is a list of 24 numbers,
# each number between 0 and 3 indicating the block index for each letter (A to Z without Q and Z).

# Letters involved: all except Q and Z
# Alphabet without Q and Z: 24 letters
letters = [chr(c) for c in range(ord('A'), ord('Z')+1) if chr(c) not in ['Q', 'Z']]
letter_to_idx = {ch: i for i, ch in enumerate(letters)}

# The four blocks have 6 letters each, total 24 letters -> each letter assigned to exactly one block
# Blocks are numbered 0,1,2,3.

words = [
    "BAKE", "ONYX", "ECHO", "OVAL",
    "GIRD", "SMUG", "JUMP", "TORN",
    "LUCK", "VINY", "LUSH", "WRAP"
]

# Decision variables:
# dice[i] = block number (0..3) assigned to letter i
dice = cp.intvar(0, 3, shape=len(letters), name="dice")

model = cp.Model()

# Each block has exactly 6 letters
for b in range(4):
    model += cp.Count(dice, b) == 6

# For each word:
# Each letter in the word must be on a different block
# Because the blocks are distinct dice, we have to use each letter from different blocks to arrange the word
# so that by picking a side on each block, we can spell the word.
for word in words:
    # convert letters to indexes
    idxs = [letter_to_idx[ch] for ch in word]
    # all dice for letters in the word are different
    model += cp.AllDifferent([dice[i] for i in idxs])

# Solve
if model.solve():
    # output a list of 24 numbers representing the block (dice) for each letter (in alphabetical order A..Z without Q,Z)
    solution = {'dice': dice.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
