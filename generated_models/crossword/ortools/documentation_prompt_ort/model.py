from ortools.sat.python import cp_model
import json

# Words given
words = [
    "HOSES", "LASER", "SHEETS", "STEER", "SAILS", "HEEL", "KEEL", "KNOT",
    "LINE", "LEE", "EEL", "HIKE", "ALE", "AFT", "TIE"
]

# Sort words first by length descending, then alphabetically ascending
words_sorted = sorted(words, key=lambda w: (-len(w), w))

# Crossword grid and clues:
# Positions 1 to 8 correspond to words starting at those locations.
# We need to assign words to these positions such that the crossword constraints hold.
# The grid is 6 rows x 5 columns.

# The grid layout with clues:
# Row 1: 1 (across), 2 (across), 3 (across)
# Row 2: 3 (down), 4 (across), 5 (across)
# Row 3: 4 (down), 5 (down), 6 (across)
# Row 4: 6 (down), 7 (across)
# Row 5: 8 (across)
# Row 6: (some black squares)

# From the puzzle:
# Across words:
# 1: Row 1, Col 1-3 (length 3)
# 2: Row 1, Col 3-5 (length 3)
# 4: Row 3, Col 2-4 (length 3)
# 5: Row 3, Col 4-5 (length 2)
# 6: Row 4, Col 1-3 (length 3)
# 7: Row 4, Col 3-5 (length 3)
# 8: Row 5, Col 1-5 (length 5)

# Down words:
# 1: Col 1, Row 1-5 (length 5)
# 2: Col 3, Row 1-3 (length 3)
# 3: Col 5, Row 1-3 (length 3)

# Let's define the words lengths for each clue:
# 1: length 5 (down), length 3 (across)
# 2: length 3 (across), length 3 (down)
# 3: length 3 (across), length 3 (down)
# 4: length 3 (across), length 3 (down)
# 5: length 2 (across), length 3 (down)
# 6: length 3 (across), length 3 (down)
# 7: length 3 (across)
# 8: length 5 (across)

# But from the puzzle, the numbers 1 to 8 correspond to the words starting at those locations.
# So the words are:
# 1: across at (1,1) length 3
# 2: across at (1,3) length 3
# 3: across at (1,5) length 3
# 4: down at (3,2) length 3
# 5: down at (3,4) length 3
# 6: across at (4,1) length 3
# 7: across at (4,3) length 3
# 8: across at (5,1) length 5

# Let's map the words to these positions and lengths:

# Positions and lengths:
positions = {
    1: 3,
    2: 3,
    3: 3,
    4: 3,
    5: 3,
    6: 3,
    7: 3,
    8: 5
}

# We will assign to each position a word index from words_sorted that matches the length.

# Create model
model = cp_model.CpModel()

# Create variables: word index assigned to each position
# Domain: indices of words with matching length
length_to_indices = {}
for i, w in enumerate(words_sorted):
    length_to_indices.setdefault(len(w), []).append(i)

pos_vars = {}
for pos, length in positions.items():
    domain = length_to_indices.get(length, [])
    pos_vars[pos] = model.NewIntVarFromDomain(cp_model.Domain.FromValues(domain), f'pos_{pos}')

# All assigned words must be different
model.AddAllDifferent([pos_vars[pos] for pos in positions])

# Now, add constraints for overlapping letters between across and down words.

# Define the grid positions for each word (row, col) zero-based indexing:
# For across words:
# 1: (0,0),(0,1),(0,2)
# 2: (0,2),(0,3),(0,4)
# 3: (0,4),(1,4),(2,4)
# 6: (3,0),(3,1),(3,2)
# 7: (3,2),(3,3),(3,4)
# 8: (4,0),(4,1),(4,2),(4,3),(4,4)

# For down words:
# 4: (2,1),(3,1),(4,1)
# 5: (2,3),(3,3),(4,3)

# Overlaps:
# pos 1 across and pos 4 down overlap at (0,1) and (2,1) ? No direct overlap
# pos 2 across and pos 4 down overlap at (0,2) and (2,1)? No
# pos 2 across and pos 5 down overlap at (0,3) and (2,3) overlap at (0,3) and (2,3) no
# pos 3 across and pos 5 down overlap at (0,4) and (2,3) no
# pos 6 across and pos 4 down overlap at (3,1) and (3,1) yes at (3,1)
# pos 7 across and pos 5 down overlap at (3,3) and (3,3) yes at (3,3)
# pos 8 across and pos 4 down overlap at (4,1) and (4,1) yes at (4,1)
# pos 8 across and pos 5 down overlap at (4,3) and (4,3) yes at (4,3)

# Let's define the overlaps with indices in the words:

# pos 6 across (3,0),(3,1),(3,2)
# pos 4 down (2,1),(3,1),(4,1)
# overlap at (3,1)
# pos 6 letter index 1 == pos 4 letter index 1

# pos 7 across (3,2),(3,3),(3,4)
# pos 5 down (2,3),(3,3),(4,3)
# overlap at (3,3)
# pos 7 letter index 1 == pos 5 letter index 1

# pos 8 across (4,0),(4,1),(4,2),(4,3),(4,4)
# pos 4 down (2,1),(3,1),(4,1)
# overlap at (4,1)
# pos 8 letter index 1 == pos 4 letter index 2

# pos 8 across (4,0),(4,1),(4,2),(4,3),(4,4)
# pos 5 down (2,3),(3,3),(4,3)
# overlap at (4,3)
# pos 8 letter index 3 == pos 5 letter index 2

# pos 1 across (0,0),(0,1),(0,2)
# pos 2 across (0,2),(0,3),(0,4)
# overlap at (0,2)
# pos 1 letter index 2 == pos 2 letter index 0

# pos 2 across (0,2),(0,3),(0,4)
# pos 3 across (0,4),(1,4),(2,4)
# overlap at (0,4)
# pos 2 letter index 2 == pos 3 letter index 0

# pos 4 down (2,1),(3,1),(4,1)
# pos 6 across (3,0),(3,1),(3,2)
# overlap at (3,1)
# already added

# pos 5 down (2,3),(3,3),(4,3)
# pos 7 across (3,2),(3,3),(3,4)
# overlap at (3,3)
# already added

# pos 3 across (0,4),(1,4),(2,4)
# pos 5 down (2,3),(3,3),(4,3)
# no overlap

# pos 1 across (0,0),(0,1),(0,2)
# pos 4 down (2,1),(3,1),(4,1)
# no overlap

# pos 1 across (0,0),(0,1),(0,2)
# pos 8 across (4,0),(4,1),(4,2),(4,3),(4,4)
# no overlap

# We need to model the letter equality constraints for these overlaps.

# Helper function to get letter variable for a word at a position
def letter_var(word_var, letter_index):
    # Create an array of variables for each letter in the word
    # We will create a 2D array: word_var x letter_index
    # But since word_var is a variable, we use Element constraints
    # We will create a matrix letters[word][letter] = ASCII code of letter
    # Then use Element to get the letter at letter_index for the assigned word_var
    return model.NewIntVar(ord('A'), ord('Z'), f'letter_{word_var}_{letter_index}')

# Precompute letters ASCII codes for all words_sorted
letters_ascii = []
max_len = max(len(w) for w in words_sorted)
for w in words_sorted:
    ascii_codes = [ord(c) for c in w]
    # pad with -1 for shorter words to avoid index error
    ascii_codes += [-1] * (max_len - len(w))
    letters_ascii.append(ascii_codes)

# Create letter variables for each position and letter index
pos_letter_vars = {}
for pos, length in positions.items():
    pos_letter_vars[pos] = []
    for i in range(length):
        var = model.NewIntVar(ord('A'), ord('Z'), f'pos{pos}_letter{i}')
        pos_letter_vars[pos].append(var)
        # Link var to the letter of the assigned word
        # Use Element constraint: pos_letter_vars[pos][i] == letters_ascii[pos_vars[pos]][i]
        # Since pos_vars[pos] is a variable, we use AddElement
        # But AddElement requires index variable and list of constants
        # We create a list of letters for letter i for all words
        letter_i_list = [letters_ascii[w][i] for w in range(len(words_sorted))]
        model.AddElement(pos_vars[pos], letter_i_list, var)

# Add overlap constraints:

# pos 6 letter 1 == pos 4 letter 1
model.Add(pos_letter_vars[6][1] == pos_letter_vars[4][1])

# pos 7 letter 1 == pos 5 letter 1
model.Add(pos_letter_vars[7][1] == pos_letter_vars[5][1])

# pos 8 letter 1 == pos 4 letter 2
model.Add(pos_letter_vars[8][1] == pos_letter_vars[4][2])

# pos 8 letter 3 == pos 5 letter 2
model.Add(pos_letter_vars[8][3] == pos_letter_vars[5][2])

# pos 1 letter 2 == pos 2 letter 0
model.Add(pos_letter_vars[1][2] == pos_letter_vars[2][0])

# pos 2 letter 2 == pos 3 letter 0
model.Add(pos_letter_vars[2][2] == pos_letter_vars[3][0])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract the assigned word indices for positions 1 to 8
    E = [solver.Value(pos_vars[pos]) for pos in range(1, 9)]
    print(json.dumps({'E': E}, indent=4))
else:
    print("No solution found.")