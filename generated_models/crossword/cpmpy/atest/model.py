from cpmpy import *
import json

# List of words
words = ["AFT", "ALE", "EEL", "HEEL", "HIKE", "KEEL", "KNOT", "LASER", "LEE", "LINE", "SAILS", "SHEET", "STEER", "TIE", "HOSES"]

# Lengths of words
word_lengths = [len(word) for word in words]

# Number of words
n_words = len(words)

# Number of positions in the crossword puzzle
n_positions = 8

# Decision variables
E = intvar(0, n_words - 1, shape=n_positions, name="E")

# Model
model = Model()

# All selected words must be distinct
model += [AllDifferent(E)]

# The selected words must fit into the crossword puzzle grid
# Define the required lengths for each position in the crossword puzzle
required_lengths = [5, 2, 2, 5, 5, 4, 3, 5]  # Based on the crossword puzzle structure

# Ensure the selected words have the correct lengths using element constraint
for i in range(n_positions):
    model += [cpm_element(word_lengths, E[i]) == required_lengths[i]]

# Solve the model
model.solve()

# Print the solution
solution = {"E": E.value().tolist()}
print(json.dumps(solution))