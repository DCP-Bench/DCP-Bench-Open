# Crossword: fill a fixed crossword grid with 8 distinct words chosen from a list of 15 words,
# so that every pair of words that cross share the same letter at the crossing cell.
import numpy as np
import cpmpy as cp


def build(instance):
    # The word list and the grid are part of the problem statement, not of the instance (the
    # instance has no fields), so they are mirrored here from the problem description.
    word_list = ["AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT",
                 "LASER", "LEE", "LINE", "SAILS", "SHEET", "STEER", "TIE"]
    # Words are numbered longest first, then alphabetically: word 0 is HOSES, ..., word 14 is TIE.
    words = sorted(word_list, key=lambda w: (-len(w), w))
    word_len = max(len(w) for w in words)
    num_words = len(words)

    # letters[w][p] = letter p of word w as a number (A=1 ... Z=26), 0 where the word is shorter
    letters = np.zeros((num_words, word_len), dtype=int)
    for w, word in enumerate(words):
        for p, ch in enumerate(word):
            letters[w, p] = ord(ch) - ord("A") + 1
    letters = cp.cpm_array(letters)

    # The 8 numbered slots of the puzzle (clue numbers 1..8 are slots 0..7).
    # Each crossing is (slot a, position in a, slot b, position in b): the letter at that
    # position of the word placed in slot a is the same cell as that of the word in slot b.
    crossings = [
        (0, 2, 1, 0),
        (0, 4, 2, 0),
        (3, 1, 1, 2),
        (3, 2, 4, 0),
        (3, 3, 2, 2),
        (6, 0, 1, 3),
        (6, 1, 4, 1),
        (6, 2, 2, 3),
        (7, 0, 5, 1),
        (7, 2, 1, 4),
        (7, 3, 4, 2),
        (7, 4, 2, 4),
    ]
    num_slots = 8

    # E[s] = index of the word selected for slot s
    E = cp.intvar(0, num_words - 1, shape=(num_slots,), name="E")

    model = cp.Model()

    # Each selected word is used in at most one slot, so the 8 slots hold different words.
    model += cp.AllDifferent(E)

    # Where two slots cross, the two words have the same letter in the shared cell.
    for a, pa, b, pb in crossings:
        model += letters[:, pa][E[a]] == letters[:, pb][E[b]]

    return model, {"E": E}
