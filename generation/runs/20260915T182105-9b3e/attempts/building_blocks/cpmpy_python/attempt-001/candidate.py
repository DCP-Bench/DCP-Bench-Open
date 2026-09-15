import cpmpy as cp


def build(instance):
    """Building blocks: work out which letters sit on which alphabet block,
    given a list of words each block set must be able to spell.
    """
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]
    num_letters = instance["num_letters"]
    alphabet = instance["alphabet"]
    words_str = instance["words_str"]

    letter_map = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_map[c] for c in word] for word in words_str]

    dice = cp.intvar(0, num_blocks - 1, shape=num_letters, name="dice")

    model = cp.Model()
    # The letters of a word must come off different blocks.
    for word in words:
        model += cp.AllDifferent([dice[letter] for letter in word])
    # Every block carries exactly num_sides letters.
    for block in range(num_blocks):
        model += cp.sum([dice[i] == block for i in range(num_letters)]) == num_sides

    return model, {"dice": dice}
