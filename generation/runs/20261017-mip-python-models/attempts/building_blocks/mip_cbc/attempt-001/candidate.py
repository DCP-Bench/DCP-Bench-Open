# Building blocks: alphabet blocks with one letter per side. Each block has num_sides
# sides, the blocks together carry every letter of the alphabet once. Arrange the blocks
# so that every word of the list can be spelled. Output dice[l] is the block of letter l.
import mip


def build(instance):
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]
    num_letters = instance["num_letters"]
    alphabet = instance["alphabet"]
    words = instance["words_str"]

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[l][b] = 1 when letter l is on block b. Each letter is on exactly one block.
    x = [[m.add_var(f"x_{l}_{b}", var_type=mip.BINARY) for b in range(num_blocks)]
         for l in range(num_letters)]
    for l in range(num_letters):
        # Each letter appears on exactly one block.
        m += mip.xsum(x[l][b] for b in range(num_blocks)) == 1

    # Each block has exactly num_sides sides, one letter per side.
    # Block b carries num_sides letters.
    for b in range(num_blocks):
        # The blocks contain every letter, each block showing num_sides letters.
        m += mip.xsum(x[l][b] for l in range(num_letters)) == num_sides

    # The dice output: the block index of each letter, an exact integer.
    dice = []
    for l in range(num_letters):
        d = m.add_var(f"dice_{l}", lb=0, ub=num_blocks - 1, var_type=mip.INTEGER)
        # The block index of letter l is the one block it sits on.
        m += d == mip.xsum(b * x[l][b] for b in range(num_blocks))
        dice.append(d)

    # Each word of the list must be spelled with the blocks: a word uses each block at most
    # once, so its letters sit on distinct blocks.
    for w in words:
        # Spell each word of the list, one letter per block, no block used twice.
        letters = [alphabet.index(ch) for ch in w]
        for b in range(num_blocks):
            m += mip.xsum(x[l][b] for l in letters) <= 1

    # Satisfaction problem: no objective.
    return m, {"dice": dice}
