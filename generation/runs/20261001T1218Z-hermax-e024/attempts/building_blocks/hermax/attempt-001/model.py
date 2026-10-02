# Building blocks: alphabet blocks each carry one letter on every side, and
# together the blocks carry every letter of the alphabet. Choose which block
# carries each letter so that every word in the list can be spelled, which
# needs its letters on different blocks.
from hermax.model import Model


def build(instance):
    alphabet = instance["alphabet"]  # the letters, in the order they are numbered
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]  # letters on each block
    num_letters = instance["num_letters"]  # one dice entry per letter
    words_str = instance["words_str"]

    # each word as the numbers of its letters
    letter_index = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_index[c] for c in word] for word in words_str]

    m = Model()
    # dice[l] = the block (numbered from 0) that carries letter l
    dice = m.int_vector("dice", num_letters, 0, num_blocks - 1)

    # the letters of a word are on different blocks
    for word in words:
        m &= m.vector([dice[letter] for letter in word]).all_different()

    # every block carries exactly num_sides letters
    for block in range(num_blocks):
        m &= (sum((dice[letter] == block) for letter in range(num_letters)) == num_sides)

    return m, {"dice": dice}
