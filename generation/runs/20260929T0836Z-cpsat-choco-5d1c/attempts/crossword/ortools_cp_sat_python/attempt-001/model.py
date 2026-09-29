# Crossword: pick 8 different words from a list of 15 to fill the 8 numbered
# slots of a small crossword grid so that every place where two slots cross
# holds the same letter in both words.
from ortools.sat.python import cp_model

# The puzzle itself is fixed by the problem, so its data is mirrored here.
# The words as letter numbers (a=1 .. z=26), padded with 0 to length 5, sorted
# longest first and then alphabetically.
WORDS = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",  # five letters
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",  # four letters
    "AFT", "ALE", "EEL", "LEE", "TIE",  # three letters
]
WORD_LEN = 5
N_SLOTS = 8
# each crossing is [slot a, letter position in a, slot b, letter position in b]
CROSSINGS = [
    [0, 2, 1, 0], [0, 4, 2, 0], [3, 1, 1, 2], [3, 2, 4, 0], [3, 3, 2, 2], [6, 0, 1, 3],
    [6, 1, 4, 1], [6, 2, 2, 3], [7, 0, 5, 1], [7, 2, 1, 4], [7, 3, 4, 2], [7, 4, 2, 4],
]


def build(instance):
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (WORD_LEN - len(word)) for word in WORDS]
    n_words = len(WORDS)

    model = cp_model.CpModel()

    # E[s] = the word (index in the list) placed in slot s; all slots get different words
    E = [model.new_int_var(0, n_words - 1, f"E_{s}") for s in range(N_SLOTS)]
    model.add_all_different(E)

    # where two slots cross, the two words show the same letter. The letter of
    # the chosen word at a position is read from the table of letters with an
    # element constraint on the word index.
    for slot_a, pos_a, slot_b, pos_b in CROSSINGS:
        letter_a = model.new_int_var(0, 26, f"letter_{slot_a}_{pos_a}")
        letter_b = model.new_int_var(0, 26, f"letter_{slot_b}_{pos_b}")
        model.add_element(E[slot_a], [word[pos_a] for word in letters], letter_a)
        model.add_element(E[slot_b], [word[pos_b] for word in letters], letter_b)
        model.add(letter_a == letter_b)

    return model, {"E": E}
