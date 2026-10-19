# Crossword: complete the 6-row by 5-column grid of the description by selecting 8 of the
# 15 given words, one for each word-start location numbered 1 to 8.
# E[k] is the index (sorted by length descending, then alphabetically) of the word that
# starts at location k+1.

import cvc5.pythonic as cz

WORDS_TEXT = [
    "AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT", "LASER", "LEE",
    "LINE", "SAILS", "SHEET", "STEER", "TIE",
]

# Word slots of the grid, in the order of the numbers 1..8 (row, column) per cell.
SLOTS = [
    # 1: across, row 1
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
    # 2: down, column 3
    [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],
    # 3: down, column 5
    [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],
    # 4: across, row 3
    [(2, 1), (2, 2), (2, 3), (2, 4)],
    # 5: down, column 4
    [(2, 3), (3, 3), (4, 3), (5, 3)],
    # 6: down, column 1
    [(3, 0), (4, 0), (5, 0)],
    # 7: across, row 4
    [(3, 2), (3, 3), (3, 4)],
    # 8: across, row 5
    [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
]


def build(instance):
    words = sorted(WORDS_TEXT, key=lambda w: (-len(w), w))
    n_words = len(words)

    E = [cz.Int(f"e{k}") for k in range(len(SLOTS))]
    cells = {}
    for slot in SLOTS:
        for rc in slot:
            if rc not in cells:
                cells[rc] = cz.Int(f"cell_{rc[0]}_{rc[1]}")

    constraints = []

    # Each chosen word is one of the 15 words, and no word is used twice.
    for e in E:
        constraints += [e >= 0, e <= n_words - 1]
    constraints.append(cz.Distinct(E))

    # Crossing cells hold letters in A..Z (ASCII 65..90).
    for v in cells.values():
        constraints += [v >= 65, v <= 90]

    # Each slot takes a word of its own length, and its letters are the letters of
    # the grid cells the slot covers.
    for k, slot in enumerate(SLOTS):
        e = E[k]
        length = len(slot)
        candidates = [w for w in range(n_words) if len(words[w]) == length]
        # A word of the slot's length: the slot's word is one of these candidates.
        constraints.append(cz.Or([e == w for w in candidates]))
        for w in candidates:
            for p, rc in enumerate(slot):
                constraints.append(cz.Implies(e == w, cells[rc] == ord(words[w][p])))

    return constraints, {"E": E}
