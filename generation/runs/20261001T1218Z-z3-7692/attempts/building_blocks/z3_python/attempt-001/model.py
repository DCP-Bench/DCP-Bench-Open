# Building blocks: spread the letters of the alphabet over alphabet blocks, a
# fixed number of letters per block, so that every listed word can be spelled
# by using one block per letter.
import z3


def build(instance):
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]    # letters on each block
    words_str = instance["words_str"]    # the words that must be spelled
    alphabet = instance["alphabet"]      # the letters on the blocks
    num_letters = instance["num_letters"]

    # Each word as a list of letter numbers (position in the alphabet string).
    letter_map = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_map[c] for c in w] for w in words_str]

    # dice[l] is the block on which letter l is placed (0..num_blocks-1).
    dice = [z3.Int(f"dice_{l}") for l in range(num_letters)]

    solver = z3.Solver()

    for d in dice:
        solver.add(d >= 0, d <= num_blocks - 1)

    # The letters of a word must be on different blocks, since a block can show
    # only one letter at a time.
    for word in words:
        solver.add(z3.Distinct([dice[letter] for letter in word]))

    # Each block carries exactly num_sides letters.
    for block in range(num_blocks):
        solver.add(z3.Sum([z3.If(d == block, 1, 0) for d in dice]) == num_sides)

    return solver, {"dice": dice}
