# Crypta: a cryptarithmetic addition of two 20-digit numbers. Each letter is a
# different digit from 0 to 9, and no number starts with a zero.
from hermax.model import Model

FIRST = "BAIJJAJIIAHFCFEBBJEA"
SECOND = "DHFGABCDIDBIFFAGFEJE"
TOTAL = "GJEGACDDHFAFJBFIHEEF"


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    letters = sorted(set(FIRST + SECOND + TOTAL))
    width = len(TOTAL)

    m = Model()
    # digit[letter] = the digit the letter stands for
    digit = {letter: m.int(letter, 0, 9) for letter in letters}
    # every letter stands for a different digit
    m &= m.vector([digit[letter] for letter in letters]).all_different()
    # no number starts with a zero
    for word in (FIRST, SECOND, TOTAL):
        m &= (digit[word[0]] != 0)

    # The addition is done column by column, from the units up. carry[k] is what
    # column k passes on to column k + 1, 0 or 1.
    carry = [m.int(f"carry_{k}", 0, 1) for k in range(width - 1)]
    for k in range(width):
        # the two digits of column k plus the carry coming in = the digit of the total
        # plus 10 * the carry going out
        left = digit[FIRST[-1 - k]] + digit[SECOND[-1 - k]]
        if k > 0:
            left = left + carry[k - 1]
        right = digit[TOTAL[-1 - k]]
        if k < width - 1:
            right = right + 10 * carry[k]
        m &= (left == right)

    return m, {letter: digit[letter] for letter in letters}
