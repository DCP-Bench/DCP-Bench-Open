# Crypta cryptarithm: replace the ten letters A..J by different digits so that
# the sum of two 20-digit numbers equals a third, none starting with a zero.
import z3


def build(instance):
    del instance  # the puzzle states its own words

    letters = "ABCDEFGHIJ"

    # Bit-vector encoding: each digit is a 4-bit vector and each column sum a
    # 5-bit vector. Z3 bit-blasts these to SAT, which proves the uniqueness of
    # the answer much faster than linear integer arithmetic over 20 columns.
    digit = {ch: z3.BitVec(ch, 4) for ch in letters}

    # The three words of the sum, most significant digit first (problem data).
    first = "BAIJJAJIIAHFCFEBBJEA"
    second = "DHFGABCDIDBIFFAGFEJE"
    result = "GJEGACDDHFAFJBFIHEEF"

    solver = z3.Solver()

    # Each letter is a digit from 0 to 9, and different letters are different digits.
    for ch in letters:
        solver.add(z3.ULE(digit[ch], 9))
    solver.add(z3.Distinct([digit[ch] for ch in letters]))

    # The first letter of each number cannot be zero.
    for word in (first, second, result):
        solver.add(digit[word[0]] != 0)

    def wide(bv):
        # Widen a 4-bit digit to 5 bits so a column sum (at most 9 + 9 + 1) fits.
        return z3.ZeroExt(1, bv)

    # Column-wise addition from the units column leftwards: carry[k] is True when
    # a 1 is carried into column k (k = 0 is the units column).
    width = len(result)
    carry = [z3.Bool(f"carry_{k}") for k in range(width + 1)]
    solver.add(z3.Not(carry[0]))  # nothing is carried into the units column
    for k in range(width):
        # Digit of a word in column k, counted from the right.
        d1 = digit[first[width - 1 - k]]
        d2 = digit[second[width - 1 - k]]
        dr = digit[result[width - 1 - k]]
        column_sum = wide(d1) + wide(d2) + z3.If(carry[k], z3.BitVecVal(1, 5), z3.BitVecVal(0, 5))
        written = wide(dr) + z3.If(carry[k + 1], z3.BitVecVal(10, 5), z3.BitVecVal(0, 5))
        solver.add(column_sum == written)
    solver.add(z3.Not(carry[width]))  # the sum has no more digits than the result

    return solver, {ch: z3.BV2Int(digit[ch]) for ch in letters}
