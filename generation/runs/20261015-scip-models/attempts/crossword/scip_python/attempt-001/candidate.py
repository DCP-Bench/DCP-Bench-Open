# Crossword: choose 8 distinct words from the list so that they fill the 8 word slots
# of the 6 x 5 grid and agree on every crossing letter.
from pyscipopt import Model, quicksum

# The 15 words, sorted from the longest and then alphabetically (problem data).
WORDS = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
    "AFT", "ALE", "EEL", "LEE", "TIE",
]

# The word slots of the grid (problem data). Each slot is (clue number, direction,
# row, column, length), with rows and columns numbered from 0.
SLOTS = [
    (1, "across", 0, 0, 5),
    (2, "down", 0, 2, 5),
    (3, "down", 0, 4, 5),
    (4, "across", 2, 1, 4),
    (5, "down", 2, 3, 4),
    (6, "down", 3, 0, 3),
    (7, "across", 3, 2, 3),
    (8, "across", 4, 0, 5),
]


def build(instance):
    m = Model()
    n_slots = len(SLOTS)
    n_words = len(WORDS)

    # cells of each slot, in reading order
    cells = []
    for _, direction, r, c, length in SLOTS:
        if direction == "across":
            cells.append([(r, c + i) for i in range(length)])
        else:
            cells.append([(r + i, c) for i in range(length)])

    # y[s, w] = 1 if slot s is filled with word w (only words of the slot's length)
    y = {}
    for s in range(n_slots):
        for w in range(n_words):
            if len(WORDS[w]) == len(cells[s]):
                y[s, w] = m.addVar(name=f"y_{s}_{w}", vtype="B")

    # each slot is filled by exactly one word
    for s in range(n_slots):
        m.addCons(quicksum(y[s, w] for w in range(n_words) if (s, w) in y) == 1)

    # the 8 selected words are distinct words from the list
    for w in range(n_words):
        m.addCons(quicksum(y[s, w] for s in range(n_slots) if (s, w) in y) <= 1)

    # crossing cells: the two slots through a cell must put the same letter there
    for cell in set(cell for slot_cells in cells for cell in slot_cells):
        through = [(s, cells[s].index(cell)) for s in range(n_slots) if cell in cells[s]]
        if len(through) < 2:
            continue
        (s, i), (t, j) = through[0], through[1]
        for letter in set(w[0] for w in WORDS):
            # a letter at position i of slot s is in the word for slot s exactly when
            # the word for slot t has the same letter at position j
            m.addCons(quicksum(y[s, w] for w in range(n_words)
                               if (s, w) in y and WORDS[w][i] == letter)
                      == quicksum(y[t, w] for w in range(n_words)
                                  if (t, w) in y and WORDS[w][j] == letter))

    # E[k] = index of the word in the clue k + 1 slot
    clue_order = sorted(range(n_slots), key=lambda s: SLOTS[s][0])
    E = [quicksum(w * y[s, w] for w in range(n_words) if (s, w) in y) for s in clue_order]
    return m, {"E": E}
