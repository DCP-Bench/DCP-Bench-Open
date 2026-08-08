
import cpmpy as cp
import json

# List of words sorted by length (descending) then alphabetically
sorted_words = [
    "HOSES", "LASER", "SHEET", "STEER",  # 5 letters
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",  # 4 letters
    "AFT", "ALE", "EEL", "LEE", "TIE"  # 3 letters
]
word_lengths = [len(word) for word in sorted_words]

# Required lengths for each of the 8 positions (positions 1-8 in order)
required_lengths = [5, 5, 5, 4, 4, 3, 3, 5]

# Decision variables: 8 variables (indices 0-7 correspond to positions 1-8)
variables = cp.intvar(0, len(sorted_words)-1, shape=8)  # Fixed: array variable

model = cp.Model()

# Constraints: each variable's word length matches the required length
for i in range(8):
    model += cp.Element(word_lengths, variables[i]) == required_lengths[i]

# All words must be distinct (no duplicates)
model += cp.AllDifferent(variables)

# Solve and print
if model.solve():
    solution = {'E': variables.value().tolist()}  # Fixed: array variable's .value()
    print(json.dumps(solution))
else:
    print("No solution found.")
