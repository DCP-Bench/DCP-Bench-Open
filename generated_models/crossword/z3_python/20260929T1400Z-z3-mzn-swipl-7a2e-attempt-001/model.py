# Crossword: pick 8 different words from a list of 15 to fill the 8 numbered
# slots of a small crossword grid so that every place where two slots cross
# holds the same letter in both words.
import z3

# The puzzle itself is fixed by the problem, so its data is mirrored here.
# The words, sorted longest first and then alphabetically.
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
    # letters as numbers (a=1 .. z=26), padded with 0 to length 5
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (WORD_LEN - len(word)) for word in WORDS]
    n_words = len(WORDS)

    solver = z3.Solver()

    # E[s] = the word (index in the list) placed in slot s; all slots get different words
    E = [z3.Int(f"E_{s}") for s in range(N_SLOTS)]
    for word in E:
        solver.add(word >= 0, word < n_words)
    solver.add(z3.Distinct(E))

    def letter_of(word, position):
        """The letter at a position of the chosen word: an If chain over the
        words, since Z3 has no element constraint."""
        value = letters[n_words - 1][position]
        for k in range(n_words - 2, -1, -1):
            value = z3.If(word == k, letters[k][position], value)
        return value

    # where two slots cross, the two words show the same letter
    for slot_a, pos_a, slot_b, pos_b in CROSSINGS:
        solver.add(letter_of(E[slot_a], pos_a) == letter_of(E[slot_b], pos_b))

    return solver, {"E": E}
