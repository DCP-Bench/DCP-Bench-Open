from ortools.sat.python import cp_model
import json

# Letters involved (all letters except Q and Z)
letters = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'
]

# Words to be spelled
words = [
    "BAKE", "ONYX", "ECHO", "OVAL",
    "GIRD", "SMUG", "JUMP", "TORN",
    "LUCK", "VINY", "LUSH", "WRAP"
]

# Map letters to indices for easy reference
letter_to_index = {letter: i for i, letter in enumerate(letters)}

# Model definition
model = cp_model.CpModel()

# Decision variables:
# dice[i] = which block (0..3) letter i is assigned to
dice = [model.NewIntVar(0, 3, f'dice_{letters[i]}') for i in range(len(letters))]

# Each block has 6 sides, so max 6 letters per block
# Count how many letters assigned to each block
for block in range(4):
    model.Add(sum(dice[i] == block for i in range(len(letters))) <= 6)

# For each word, all letters must be on different blocks (since each letter must come from a different block)
# Because to spell a word, each letter must come from a different block (one letter per block)
# So letters in the same word must be assigned to distinct blocks
for word in words:
    indices = [letter_to_index[ch] for ch in word]
    # All different blocks for letters in the word
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            model.Add(dice[indices[i]] != dice[indices[j]])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Output the dice assignments as a list of integers in the order of letters
    solution = [solver.Value(d) for d in dice]
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")