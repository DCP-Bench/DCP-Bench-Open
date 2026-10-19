# Building blocks: alphabet blocks with one letter per side. Place every letter on
# a block so that each block carries num_sides letters, and each word can be spelt
# by a sequence of distinct blocks, one block per letter.

import cvc5.pythonic as cz


def build(instance):
    alphabet = instance["alphabet"]
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]
    num_letters = instance["num_letters"]
    words = instance["words_str"]

    dice = cz.Ints(" ".join(f"d_{k}" for k in range(num_letters)))
    if num_letters == 1:
        dice = [dice]

    constraints = []

    # Each letter is placed on one block, between 0 and num_blocks-1.
    for k in range(num_letters):
        constraints.append(dice[k] >= 0)
        constraints.append(dice[k] <= num_blocks - 1)

    # Each block has exactly num_sides letters.
    for b in range(num_blocks):
        constraints.append(
            cz.Sum([cz.If(dice[k] == b, 1, 0) for k in range(num_letters)]) == num_sides
        )

    # Every word of the list can be spelt with its letters on distinct blocks.
    for w, word in enumerate(words):
        if len(word) < 2:
            continue
        idx = [alphabet.index(ch) for ch in word]
        pos = cz.Ints(" ".join(f"p_{w}_{p}" for p in range(len(word))))
        if len(word) == 1:
            pos = [pos]
        for p in range(len(word)):
            constraints.append(pos[p] >= 0)
            constraints.append(pos[p] <= num_blocks - 1)
            constraints.append(dice[idx[p]] == pos[p])
        # The letters of one word sit on distinct blocks.
        constraints.append(cz.Distinct(list(pos)))

    return constraints, {"dice": dice}
