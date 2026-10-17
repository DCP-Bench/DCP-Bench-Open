# Cryptarithmetic puzzle: the 20-letter word LINE1 plus the 20-letter word LINE2 equals the
# 20-letter word RESULT. All letters A..J are distinct digits from 0 to 9, and the first
# letter of each number (B, D, G) cannot be zero. Output the digit of each letter.
# Method: an integer digit per letter, tied to a one-hot binary block (all different), then
# a column-by-column addition with carries, read from the last letter to the first.
import mip

LINE1 = "BAIJJAJIIAHFCFEBBJEA"
LINE2 = "DHFGABCDIDBIFFAGFEJE"
RESULT = "GJEGACDDHFAFJBFIHEEF"
LETTERS = "ABCDEFGHIJ"


def build(instance):
    N = len(RESULT)
    leading = [LINE1[0], LINE2[0], RESULT[0]]

    m = mip.Model(solver_name="CBC")
    m.verbose = 0
    m.max_mip_gap = 0.0
    m.max_mip_gap_abs = 0.0

    # digit of each letter, and a one-hot block of binaries per letter
    x = {L: m.add_var(f"x_{L}", lb=0, ub=9, var_type=mip.INTEGER) for L in LETTERS}
    p = {(L, d): m.add_var(f"p_{L}_{d}", var_type=mip.BINARY) for L in LETTERS for d in range(10)}

    # each letter takes exactly one digit, and the digit is the one its block selects
    for L in LETTERS:
        m += mip.xsum(p[L, d] for d in range(10)) == 1
        m += x[L] == mip.xsum(d * p[L, d] for d in range(10))

    # the letters are distinct digits from 0 to 9: each digit is used by at most one letter
    for d in range(10):
        m += mip.xsum(p[L, d] for L in LETTERS) <= 1

    # the first letter of each number cannot be zero
    for L in leading:
        m += p[L, 0] == 0

    # the carry into column k (column 0 is the last letter); no carry comes in at column 0
    # and none goes out of the top column, since the result has the same length as the addends
    carry = [m.add_var(f"c_{k}", lb=0, ub=2, var_type=mip.INTEGER) for k in range(N + 1)]
    m += carry[0] == 0
    m += carry[N] == 0

    # the sum of the two words equals the third word, column by column:
    # addend1 + addend2 + carry in = result + 10 * carry out
    for k in range(N):
        coef = {}
        for word, sign in ((LINE1, 1), (LINE2, 1), (RESULT, -1)):
            L = word[len(word) - 1 - k]
            coef[L] = coef.get(L, 0) + sign
        m += mip.xsum(c * x[L] for L, c in coef.items()) + carry[k] - 10 * carry[k + 1] == 0

    return m, {L: x[L] for L in LETTERS}
