# Building blocks: alphabet blocks carry one letter on each side and together hold
# every letter of the alphabet. Decide which block each letter sits on so that every
# word of the list can be spelled, which needs the letters of a word on different blocks.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    num_blocks = instance["num_blocks"]  # number of blocks (dice)
    num_sides = instance["num_sides"]    # letters on each block
    alphabet = instance["alphabet"]      # the letters, in the order the output uses
    num_letters = instance["num_letters"]
    letter_index = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_index[c] for c in word] for word in instance["words_str"]]

    pool = IDPool()
    # dice[l] = the block (0-indexed) that letter l is placed on
    dice = [Integer(f"dice{l}", 0, num_blocks - 1, vpool=pool) for l in range(num_letters)]
    engine = IntegerEngine(vars=dice, vpool=pool)

    # the letters of a word must be on different blocks, since a block shows one letter
    for word in words:
        engine.add_alldifferent([dice[letter] for letter in word])
    cnf = engine.clausify()

    # every block carries exactly num_sides letters
    for block in range(num_blocks):
        cnf.extend(CardEnc.equals(lits=[dice[letter].equals(block) for letter in range(num_letters)],
                                  bound=num_sides, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"dice": dice}
