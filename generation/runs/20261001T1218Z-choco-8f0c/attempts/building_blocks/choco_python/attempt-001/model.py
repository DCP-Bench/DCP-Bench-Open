# Building blocks: put each letter of the alphabet on one side of a block, with the
# same number of sides on every block, so that every word in the list can be
# spelled by taking its letters from different blocks.
from pychoco.model import Model


def build(instance):
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]  # letters on each block
    num_letters = instance["num_letters"]  # letters of the alphabet used on the blocks
    alphabet = instance["alphabet"]  # the letters, in order; letter i is alphabet[i]
    words_str = instance["words_str"]  # the words to be spelled

    # position of each letter in the alphabet, and each word as a list of positions
    letter_map = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_map[c] for c in word] for word in words_str]

    model = Model()

    # dice[l] = the block on which letter l is placed (0..num_blocks-1)
    dice = [model.intvar(0, num_blocks - 1, name=f"dice_{l}") for l in range(num_letters)]

    # the letters of a word must be on different blocks (a block shows one letter at a time)
    for word in words:
        model.all_different([dice[letter] for letter in word]).post()

    # there are exactly num_sides letters on each block
    # (pychoco takes the occurrence counts as variables, here fixed to num_sides)
    model.global_cardinality(dice, list(range(num_blocks)),
                             [model.intvar(num_sides, num_sides) for _ in range(num_blocks)]).post()

    return model, {"dice": dice}
