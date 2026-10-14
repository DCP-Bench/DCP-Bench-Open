# Crossword: pick 8 different words from a list of 15 to fill the 8 numbered
# slots of a small crossword grid so that every place where two slots cross
# holds the same letter in both words.
from exact import Exact

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
    # letters as numbers (A=1 .. Z=26), padded with 0 to length 5
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (WORD_LEN - len(word)) for word in WORDS]
    n_words = len(WORDS)

    solver = Exact()
    E = [f"E_{s}" for s in range(N_SLOTS)]
    # uses[s][w] is 1 when slot s holds word w
    uses = [[f"uses_{s}_{w}" for w in range(n_words)] for s in range(N_SLOTS)]
    for s in range(N_SLOTS):
        solver.addVariable(E[s], 0, n_words - 1)
        for name in uses[s]:
            solver.addVariable(name, 0, 1)
        # every slot holds exactly one word, and E[s] is its index
        solver.addConstraint([(1, name) for name in uses[s]], True, 1, True, 1)
        solver.addConstraint([(w, uses[s][w]) for w in range(1, n_words)] + [(-1, E[s])], True, 0, True, 0)
    # all slots get different words
    for w in range(n_words):
        solver.addConstraint([(1, uses[s][w]) for s in range(N_SLOTS)], False, 0, True, 1)

    # where two slots cross, the two words show the same letter: forbid every
    # pair of words that disagree at that crossing
    for slot_a, pos_a, slot_b, pos_b in CROSSINGS:
        for word_a in range(n_words):
            for word_b in range(n_words):
                if letters[word_a][pos_a] != letters[word_b][pos_b]:
                    solver.addConstraint([(1, uses[slot_a][word_a]), (1, uses[slot_b][word_b])],
                                         False, 0, True, 1)

    return solver, {"E": E}
