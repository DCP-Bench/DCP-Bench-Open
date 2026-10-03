"""Crossword: choose 8 of 15 given words for the 8 numbered slots of a fixed grid so that the
letters agree wherever two slots cross.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. The word list, the grid and its crossings are fixed by
    # the problem statement and mirrored from the reference. Letters are coded a = 1 .. z = 26,
    # and 0 pads a word shorter than five letters.
    letter = {chr(ord("a") + k): k + 1 for k in range(26)}
    words = ["hoses", "laser", "sails", "sheet", "steer", "heel", "hike", "keel", "knot",
             "line", "aft", "ale", "eel", "lee", "tie"]
    word_len = 5
    table = [[letter[ch] for ch in word] + [0] * (word_len - len(word)) for word in words]

    # Each crossing [slot1, pos1, slot2, pos2]: letter pos1 of the word in slot1 equals
    # letter pos2 of the word in slot2.
    overlapping = [
        [0, 2, 1, 0],  # s
        [0, 4, 2, 0],  # s
        [3, 1, 1, 2],  # i
        [3, 2, 4, 0],  # k
        [3, 3, 2, 2],  # e
        [6, 0, 1, 3],  # l
        [6, 1, 4, 1],  # e
        [6, 2, 2, 3],  # e
        [7, 0, 5, 1],  # l
        [7, 2, 1, 4],  # s
        [7, 3, 4, 2],  # e
        [7, 4, 2, 4],  # r
    ]
    num_words = len(table)
    slots = range(8)
    word_ids = range(num_words)

    model = Model("crossword")

    # put[s, w] is 1 when word w fills slot s; every slot holds one word.
    put = {(s, w): model.binary_var(name=f"put_{s}_{w}") for s in slots for w in word_ids}
    for s in slots:
        model.add_constraint(model.sum(put[s, w] for w in word_ids) == 1)
    # The selected words are all different: no word fills two slots.
    for w in word_ids:
        model.add_constraint(model.sum(put[s, w] for s in slots) <= 1)

    # E[s] is the number of the word in slot s.
    E = [model.integer_var(0, num_words - 1, name=f"E_{s}") for s in slots]
    for s in slots:
        model.add_constraint(E[s] == model.sum(w * put[s, w] for w in word_ids))

    # Where two slots cross, the two words have the same letter: the letter at a position of
    # a slot is the table entry of the chosen word, so the difference of the two letters,
    # summed over the choices, is zero.
    for s1, p1, s2, p2 in overlapping:
        model.add_constraint(
            model.sum(table[w][p1] * put[s1, w] for w in word_ids)
            - model.sum(table[w][p2] * put[s2, w] for w in word_ids) == 0)

    return model, {"E": E}
