# Building blocks: each letter of the alphabet (here 24 letters, no Q or Z)
# sits on exactly one block, and each block shows num_sides letters. Every
# word in the list must be spellable, so its letters sit on distinct blocks.
from paramita.modelling import Bool


def build(instance):
    alphabet = instance["alphabet"]
    num_blocks, num_sides = instance["num_blocks"], instance["num_sides"]
    words = instance["words_str"]
    letters = list(alphabet)

    # one-hot block per letter: y[l][b] is true when letter l is on block b
    y = [[Bool(f"y_{l}_{b}") for b in range(num_blocks)] for l in range(len(letters))]
    cons = []

    # each letter is on exactly one block
    cons += [sum(y[l]) == 1 for l in range(len(letters))]

    # each block has num_sides letters, one per side
    cons += [sum(y[l][b] for l in range(len(letters))) == num_sides for b in range(num_blocks)]

    # each word's letters are on distinct blocks, so the word can be spelled
    # by turning the blocks in turn to show its letters
    for word in words:
        idx = sorted({letters.index(ch) for ch in word})
        cons += [sum(y[l][b] for l in idx) <= 1 for b in range(num_blocks)]

    # dice[l]: the block that carries letter l, in alphabet order
    dice = [sum(b * y[l][b] for b in range(num_blocks)) for l in range(len(letters))]
    return cons, {"dice": dice}
