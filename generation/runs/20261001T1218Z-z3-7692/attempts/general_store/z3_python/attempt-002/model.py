# General store: a shopkeeper's sign shows sixteen words that add up to the word
# ALLWOOL. Each different letter stands for a different digit; find the digits.
import z3


def build(instance):
    del instance  # the puzzle states its own words

    letters = "CHESABOWPL"

    # Bit-vector encoding: each digit is a 4-bit vector, column sums are 8-bit
    # vectors. Z3 bit-blasts these to SAT; a single integer equation with
    # sixteen weighted words did not finish within the time limit.
    digit = {ch: z3.BitVec(ch, 4) for ch in letters}

    # Problem data: the words above the line, and their total below it.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL",
             "BASS", "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE",
             "CHSOAP", "SHEEP"]
    total = "ALLWOOL"

    solver = z3.Solver()

    # Each letter is a digit from 0 to 9, and different letters are different digits.
    for ch in letters:
        solver.add(z3.ULE(digit[ch], 9))
    solver.add(z3.Distinct([digit[ch] for ch in letters]))

    def wide(bv):
        # Widen a 4-bit value to 8 bits so that column sums cannot overflow:
        # sixteen digits of at most 9 plus a carry of at most 15 stay below 256.
        return z3.ZeroExt(4, bv)

    # The words add up to ALLWOOL, column by column from the units column.
    # carry[k] is the amount carried into column k (at most 15 here).
    width = len(total)
    carry = [z3.BitVec(f"carry_{k}", 4) for k in range(width + 1)]
    solver.add(carry[0] == 0)  # nothing is carried into the units column
    for k in range(width):
        # The digit of each word that has a letter in column k (counted from the right).
        column = [digit[w[len(w) - 1 - k]] for w in words if k < len(w)]
        column_sum = z3.Sum([wide(d) for d in column]) + wide(carry[k])
        written = wide(digit[total[width - 1 - k]]) + 10 * wide(carry[k + 1])
        solver.add(column_sum == written)
    solver.add(carry[width] == 0)  # ALLWOOL has no more digits than its seven

    return solver, {ch: z3.BV2Int(digit[ch]) for ch in letters}
