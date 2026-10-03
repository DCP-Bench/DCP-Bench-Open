"""Crossword: choose a different word from a list of 15 for each of the 8 slots so that crossing slots share their letter."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the word list (longest first, then alphabetical,
    # letters a=1..z=26, padded with 0), the 8 slots and their 12 crossings are the
    # puzzle's own, mirrored from the reference.
    words = ["hoses", "laser", "sails", "sheet", "steer", "heel", "hike", "keel", "knot",
             "line", "aft", "ale", "eel", "lee", "tie"]
    word_len = 5
    letters = [[ord(ch) - ord("a") + 1 for ch in w] + [0] * (word_len - len(w)) for w in words]
    # (slot 1, position in slot 1, slot 2, position in slot 2): the two letters are equal.
    overlapping = [
        [0, 2, 1, 0], [0, 4, 2, 0],
        [3, 1, 1, 2], [3, 2, 4, 0], [3, 3, 2, 2],
        [6, 0, 1, 3], [6, 1, 4, 1], [6, 2, 2, 3],
        [7, 0, 5, 1], [7, 2, 1, 4], [7, 3, 4, 2], [7, 4, 2, 4],
    ]
    n_slots = 8
    slots = range(n_slots)
    word_ids = range(len(words))

    model = gp.Model("crossword")

    # uses[s, w] is 1 when slot s holds word w.
    uses = model.addVars(slots, word_ids, vtype=GRB.BINARY, name="uses")
    for s in slots:
        model.addConstr(uses.sum(s, "*") == 1, name=f"one_word[{s}]")

    # The selected words are all different.
    for w in word_ids:
        model.addConstr(uses.sum("*", w) <= 1, name=f"different[{w}]")

    # The letter at position p of the word in slot s.
    def letter(s, p):
        return gp.quicksum(letters[w][p] * uses[s, w] for w in word_ids)

    # Crossing slots have the same letter where they cross.
    for k, (s1, p1, s2, p2) in enumerate(overlapping):
        model.addConstr(letter(s1, p1) == letter(s2, p2), name=f"cross[{k}]")

    # E[s]: the index of the word in slot s.
    return model, {"E": [gp.quicksum(w * uses[s, w] for w in word_ids) for s in slots]}
