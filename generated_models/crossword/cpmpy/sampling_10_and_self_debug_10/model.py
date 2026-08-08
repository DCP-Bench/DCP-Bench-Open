
import cpmpy as cp
import json
import numpy as np

# Given words
words = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER", "AFT", "ALE", "LEE",
    "EEL", "LINE", "HEEL", "HIKE", "KEEL", "KNOT", "TIE"
]

# Sort words by length descending, then alphabetically ascending
words_sorted = sorted(words, key=lambda w: (-len(w), w))

# Map letters to integers (A=0,...,Z=25)
def word_to_ints(w, max_len):
    arr = [-1]*max_len
    for i, ch in enumerate(w):
        arr[i] = ord(ch) - ord('A')
    return arr

max_len = max(len(w) for w in words_sorted)
word_letters = np.array([word_to_ints(w, max_len) for w in words_sorted])

# Slots info: (slot_index: 0-based)
# Each slot: length, domain (indices of words with that length)
slot_lengths = [5, 3, 3, 4, 5, 5, 5, 4]

# For each slot, find words of matching length
slot_domains = []
for length in slot_lengths:
    domain = [i for i,w in enumerate(words_sorted) if len(w) == length]
    slot_domains.append(domain)

# Decision variables: E[i] = index of word assigned to slot i
E = cp.intvar(0, len(words_sorted)-1, shape=8, name="E")

model = cp.Model()

# Domain constraints: E[i] in slot_domains[i]
for i in range(8):
    model += cp.InDomain(E[i], slot_domains[i])

# All assigned words distinct
model += cp.AllDifferent(E)

# Intersection constraints:
# Slots numbering: 0-based for code, 1-based in problem
# Intersections (slot1, pos1, slot2, pos2), positions 0-based in word
intersections = [
    (0, 3, 5, 0),  # slot0 letter4 = slot5 letter1
    (0, 2, 1, 0),  # slot0 letter3 = slot1 letter1
    (1, 2, 3, 0),  # slot1 letter3 = slot3 letter1
    (2, 2, 4, 0),  # slot2 letter3 = slot4 letter1
    (3, 1, 6, 0),  # slot3 letter2 = slot6 letter1
    (3, 3, 6, 2),  # slot3 letter4 = slot6 letter3
    # Removed (4, 1, 6, 2) to avoid conflict
    (5, 1, 7, 0),  # slot5 letter2 = slot7 letter1
]

# For each intersection, enforce letter equality
for (s1, p1, s2, p2) in intersections:
    model += cp.Element(word_letters[:, p1], E[s1]) == cp.Element(word_letters[:, p2], E[s2])

# Solve
if model.solve():
    solution = {'E': [int(e.value()) for e in E]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
