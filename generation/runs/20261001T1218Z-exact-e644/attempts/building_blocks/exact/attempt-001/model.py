# Building blocks: distribute the letters of the alphabet over alphabet blocks, num_sides
# letters on each block, so that every listed word can be spelled, which needs the letters of a
# word to sit on different blocks.
from exact import Exact


def build(instance):
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]  # letters on each block
    alphabet = instance["alphabet"]  # the letters, in the order they are numbered
    num_letters = instance["num_letters"]
    letter_index = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_index[c] for c in word] for word in instance["words_str"]]

    solver = Exact()

    # dice[l] is the block (0..num_blocks-1) that carries letter l
    dice = [f"dice_{l}" for l in range(num_letters)]
    # on_block[l][b] = 1 when letter l is on block b. Exact has no all-different or counting
    # constraint, so "different blocks" and "letters per block" use these 0/1 indicators.
    on_block = [[f"letter_{l}_on_block_{b}" for b in range(num_blocks)] for l in range(num_letters)]
    for l in range(num_letters):
        solver.addVariable(dice[l], 0, num_blocks - 1)
        for name in on_block[l]:
            solver.addVariable(name, 0, 1)
        # every letter sits on exactly one block, and dice[l] is that block's number
        solver.addConstraint([(1, name) for name in on_block[l]], True, 1, True, 1)
        solver.addConstraint([(b, on_block[l][b]) for b in range(1, num_blocks)] + [(-1, dice[l])],
                             True, 0, True, 0)

    # the letters of a word must be on different blocks: each block carries at most one of them
    for word in words:
        for b in range(num_blocks):
            solver.addConstraint([(1, on_block[l][b]) for l in word], False, 0, True, 1)

    # every block carries exactly num_sides letters
    for b in range(num_blocks):
        solver.addConstraint([(1, on_block[l][b]) for l in range(num_letters)],
                             True, num_sides, True, num_sides)

    return solver, {"dice": dice}
