
import cpmpy as cp
import json

# Words given
words = [
    "HOSES", "LASER", "SHEETS", "STEER", "SAILS", "HEEL", "KEEL", "KNOT",
    "LINE", "LEE", "HIKE", "EEL", "ALE", "AFT", "TIE"
]

# Sort words first by length descending, then alphabetically ascending
words_sorted = sorted(words, key=lambda w: (-len(w), w))

# The puzzle grid and clues:
# Positions 1 to 8 correspond to words starting at those locations.
# We need to assign words to these positions such that the crossword fits.
# The grid is:
#  1   2   3   4   5
# +---+---+---+---+---+
#1| 1 |   | 2 |   | 3 |
# +---+---+---+---+---+
#2| # | # | 4 | # | 5 |
# +---+---+---+---+---+
#3| # | 4 |   | 5 |   |
# +---+---+---+---+---+
#4| 6 | # | 7 |   |   |
# +---+---+---+---+---+
#5| 8 |   |   |   |   |
# +---+---+---+---+---+
#6|   | # | # |   | # |
# +---+---+---+---+---+

# Words start at positions 1 to 8:
# 1: Across at (1,1) length 5
# 2: Across at (1,3) length 3
# 3: Across at (1,5) length 3
# 4: Down at (2,3) length 4
# 5: Down at (2,5) length 4
# 6: Across at (4,1) length 4
# 7: Across at (4,3) length 3
# 8: Down at (5,1) length 4

# We will create variables for each position, domain is indices of words with correct length

# Map position to length and orientation
positions = {
    1: ("across", 5),
    2: ("across", 3),
    3: ("across", 3),
    4: ("down", 4),
    5: ("down", 4),
    6: ("across", 4),
    7: ("across", 3),
    8: ("down", 4),
}

# Filter words by length for each position
length_to_words = {}
for w in words_sorted:
    length_to_words.setdefault(len(w), []).append(w)

# Create variables for each position with domain as indices of words of correct length
pos_vars = {}
for pos, (orient, length) in positions.items():
    domain_words = length_to_words[length]
    # domain is indices of these words in words_sorted
    domain_indices = [words_sorted.index(w) for w in domain_words]
    pos_vars[pos] = cp.intvar(min(domain_indices), max(domain_indices), name=f"pos{pos}")

# Model
model = cp.Model()

# Constraint: all words assigned are different
model += cp.AllDifferent(list(pos_vars.values()))

# Helper function to get letter at position in word
def letter(word, idx):
    return word[idx]

# We need to enforce the crossing constraints:
# From the grid, the crossing letters must be equal.

# Positions and their coordinates (row, col) for each letter:
# Position 1 (across, length 5) at (1,1) to (1,5)
pos1_coords = [(1,1),(1,2),(1,3),(1,4),(1,5)]
# Position 2 (across, length 3) at (1,3) to (1,5)
pos2_coords = [(1,3),(1,4),(1,5)]
# Position 3 (across, length 3) at (1,5) to (1,7) but grid only 5 cols, so (1,5) to (1,7) invalid
# Actually position 3 is at (1,5) length 3 across, but grid only 5 columns, so length 3 means (1,5),(1,6),(1,7) invalid
# So position 3 must be length 3 but only 5 columns, so likely length 3 means (1,5),(2,5),(3,5) down? No, position 3 is across at (1,5) length 3, but grid only 5 columns.
# The puzzle shows position 3 at (1,5) across length 3, but grid only 5 columns, so length 3 across is impossible.
# Possibly a typo or position 3 is length 3 down? The problem states position 3 is across at (1,5) length 3.
# Let's assume position 3 is across at (1,5) length 3, so columns 5,6,7 but grid only 5 columns.
# So position 3 is length 3 across at (1,5) means columns 5,6,7, but grid only 5 columns.
# So position 3 must be length 3 down at (1,5)? The problem states position 3 is across at (1,5).
# Let's check the problem statement carefully:
# The puzzle grid shows position 3 at (1,5) across length 3.
# The grid is 5 columns wide, so length 3 across from column 5 is impossible.
# So position 3 must be length 3 down at (1,5).
# Let's assume position 3 is down at (1,5) length 3.

# Let's redefine positions with orientation and length from the puzzle:
# 1: across (1,1) length 5
# 2: across (1,3) length 3
# 3: down (1,5) length 3
# 4: down (2,3) length 4
# 5: down (2,5) length 4
# 6: across (4,1) length 4
# 7: across (4,3) length 3
# 8: down (5,1) length 4

positions = {
    1: ("across", 5, (1,1)),
    2: ("across", 3, (1,3)),
    3: ("down", 3, (1,5)),
    4: ("down", 4, (2,3)),
    5: ("down", 4, (2,5)),
    6: ("across", 4, (4,1)),
    7: ("across", 3, (4,3)),
    8: ("down", 4, (5,1)),
}

# Update pos_vars domains accordingly
pos_vars = {}
for pos, (orient, length, start) in positions.items():
    domain_words = length_to_words[length]
    domain_indices = [words_sorted.index(w) for w in domain_words]
    pos_vars[pos] = cp.intvar(min(domain_indices), max(domain_indices), name=f"pos{pos}")

model = cp.Model()
model += cp.AllDifferent(list(pos_vars.values()))

# Function to get letter variable for a position and letter index
# We'll create letter variables for each position and letter index
letters_vars = {}
for pos, (orient, length, start) in positions.items():
    letters_vars[pos] = [cp.intvar(ord('A'), ord('Z'), name=f"l{pos}_{i}") for i in range(length)]

# Link letters_vars to the word assigned at pos_vars[pos]
# For each letter position, letters_vars[pos][i] == ord(word[pos_vars[pos]][i])
for pos, (orient, length, start) in positions.items():
    for i in range(length):
        # Create table of possible letters for each word in domain
        domain_words = length_to_words[length]
        domain_indices = [words_sorted.index(w) for w in domain_words]
        # For each word in domain, letter at i
        table = []
        for widx in domain_indices:
            w = words_sorted[widx]
            table.append([widx, ord(w[i])])
        # Constraint: (pos_vars[pos], letters_vars[pos][i]) in table
        model += cp.Table([pos_vars[pos], letters_vars[pos][i]], table)

# Now add crossing constraints: letters at crossing cells must be equal
# We find crossing cells by coordinates

# Build a map from coordinates to (pos, letter_index)
coord_map = {}
for pos, (orient, length, (r,c)) in positions.items():
    for i in range(length):
        rr = r + (i if orient == "down" else 0)
        cc = c + (i if orient == "across" else 0)
        coord_map.setdefault((rr,cc), []).append((pos,i))

# For each coordinate with more than one letter, enforce equality
for coord, pos_list in coord_map.items():
    if len(pos_list) > 1:
        # All letters at this coordinate must be equal
        first_pos, first_i = pos_list[0]
        for other_pos, other_i in pos_list[1:]:
            model += (letters_vars[first_pos][first_i] == letters_vars[other_pos][other_i])

# Solve
if model.solve():
    # Extract the assigned words indices for positions 1 to 8
    assigned_indices = [int(pos_vars[pos].value()) for pos in range(1,9)]
    # Print as list of 8 integers starting from 0 (indices in words_sorted)
    solution = {'E': assigned_indices}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
