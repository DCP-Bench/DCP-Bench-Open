# Crypta cryptarithm: replace the ten letters A..J by different digits so that
# the sum of two 20-digit numbers equals a third, none starting with a zero.
import z3


def build(instance):
    del instance  # the puzzle states its own words

    letters = "ABCDEFGHIJ"
    digit = {ch: z3.Int(ch) for ch in letters}

    # The three words of the sum, most significant digit first (problem data).
    first = "BAIJJAJIIAHFCFEBBJEA"
    second = "DHFGABCDIDBIFFAGFEJE"
    result = "GJEGACDDHFAFJBFIHEEF"

    solver = z3.Solver()

    # Each letter is a digit from 0 to 9, and different letters are different digits.
    for ch in letters:
        solver.add(digit[ch] >= 0, digit[ch] <= 9)
    solver.add(z3.Distinct([digit[ch] for ch in letters]))

    # The first letter of each number cannot be zero.
    for word in (first, second, result):
        solver.add(digit[word[0]] >= 1)

    # Column-wise addition from the units column leftwards: carry[k] is the carry
    # into column k (k = 0 is the units column). Columns are used instead of one
    # big equation so that the solver only sees small coefficients.
    width = len(result)
    carry = [z3.Int(f"carry_{k}") for k in range(width + 1)]
    for c in carry:
        solver.add(c >= 0, c <= 1)
    solver.add(carry[0] == 0)  # nothing is carried into the units column
    for k in range(width):
        # Digit of a word in column k, counted from the right.
        d1 = digit[first[width - 1 - k]]
        d2 = digit[second[width - 1 - k]]
        dr = digit[result[width - 1 - k]]
        solver.add(d1 + d2 + carry[k] == dr + 10 * carry[k + 1])
    solver.add(carry[width] == 0)  # the sum has no more digits than the result

    return solver, {ch: digit[ch] for ch in letters}
