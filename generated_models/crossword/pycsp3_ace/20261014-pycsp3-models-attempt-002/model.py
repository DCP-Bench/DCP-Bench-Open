from pycsp3 import *

# Crossword: a 6 by 5 grid with black squares. We choose one word from the list
# for each of the 8 numbered entries so that the entries cross consistently.
# Words are numbered as in the description: longest first, then alphabetically.
words = ["HOSES", "LASER", "SAILS", "SHEET", "STEER",
         "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
         "AFT", "ALE", "EEL", "LEE", "TIE"]

# length of the entry with number 1 to 8 in the grid
entry_length = [5, 5, 5, 4, 4, 3, 3, 5]

# the word chosen for each entry; ACE rejects the identifier E, so the
# variables get another name and the output E is an alias for them
chosen = VarArray(size=8, dom=range(len(words)))
E = chosen

# candidate words for each entry: the words with the length of that entry
candidates = [[i for i, w in enumerate(words) if len(w) == entry_length[k]] for k in range(8)]

# (entry, position, other entry, position) for every square where two entries cross
crossings = [
    (0, 2, 1, 0), (0, 4, 2, 0), (1, 2, 3, 1), (1, 3, 6, 0), (1, 4, 7, 2), (2, 2, 3, 3),
    (2, 3, 6, 2), (2, 4, 7, 4), (3, 2, 4, 0), (4, 1, 6, 1), (4, 2, 7, 3), (5, 1, 7, 0),
]

satisfy(
    # each entry takes a word of its own length
    [chosen[k] in set(candidates[k]) for k in range(8)],
    # the chosen words are all different
    AllDifferent(chosen),
    # the letters where two entries cross must agree
    [
        Table(scope=[chosen[a], chosen[b]], supports=[
            (i, j) for i in candidates[a] for j in candidates[b]
            if words[i][p] == words[j][q]
        ])
        for a, p, b, q in crossings
    ],
)
