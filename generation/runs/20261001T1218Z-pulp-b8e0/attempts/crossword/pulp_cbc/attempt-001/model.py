"""Crossword: choose 8 different words from a list of 15 for the 8 numbered slots of a small
crossword grid so that wherever two slots cross they share the same letter.

The model reports the word chosen for each slot (E), numbering the words longest first and
then alphabetically: HOSES is 0, LASER 1, ..., TIE 14.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its word list and grid are below

    # The word list, as letters 1..26 padded with 0 to five places, mirrored from the
    # reference.
    words = ["HOSES", "LASER", "SAILS", "SHEET", "STEER", "HEEL", "HIKE", "KEEL", "KNOT",
             "LINE", "AFT", "ALE", "EEL", "LEE", "TIE"]
    word_len = 5
    letters = [[ord(ch) - ord("A") + 1 for ch in w] + [0] * (word_len - len(w)) for w in words]
    num_words = len(words)

    # Where the slots cross, from the grid of the puzzle: [slot1, place1, slot2, place2]
    # means letter place1 of the word in slot1 is letter place2 of the word in slot2.
    overlapping = [
        [0, 2, 1, 0], [0, 4, 2, 0],
        [3, 1, 1, 2], [3, 2, 4, 0], [3, 3, 2, 2],
        [6, 0, 1, 3], [6, 1, 4, 1], [6, 2, 2, 3],
        [7, 0, 5, 1], [7, 2, 1, 4], [7, 3, 4, 2], [7, 4, 2, 4],
    ]
    n = 8  # number of slots

    problem = pulp.LpProblem("crossword", pulp.LpMinimize)  # satisfaction

    # put[s][w] = 1 if word w fills slot s; every slot gets one word
    put = [[pulp.LpVariable(f"put_{s}_{w}", cat="Binary") for w in range(num_words)]
           for s in range(n)]
    for s in range(n):
        problem += pulp.lpSum(put[s]) == 1

    # the selected words are all different
    for w in range(num_words):
        problem += pulp.lpSum(put[s][w] for s in range(n)) <= 1

    # where two slots cross, the letter of one word equals the letter of the other
    def letter(slot, place):
        return pulp.lpSum(letters[w][place] * put[slot][w] for w in range(num_words))

    for s1, p1, s2, p2 in overlapping:
        problem += letter(s1, p1) == letter(s2, p2)

    E = [pulp.lpSum(w * put[s][w] for w in range(num_words)) for s in range(n)]
    return problem, {"E": E}
