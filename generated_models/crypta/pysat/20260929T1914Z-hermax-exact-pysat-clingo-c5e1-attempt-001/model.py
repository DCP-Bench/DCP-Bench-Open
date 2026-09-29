# Crypta: a cryptarithmetic addition of two 20-digit numbers. Each letter is a
# different digit from 0 to 9, and no number starts with a zero.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

FIRST = "BAIJJAJIIAHFCFEBBJEA"
SECOND = "DHFGABCDIDBIFFAGFEJE"
TOTAL = "GJEGACDDHFAFJBFIHEEF"


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    letters = sorted(set(FIRST + SECOND + TOTAL))
    width = len(TOTAL)

    pool = IDPool()
    # digit[letter] = the digit the letter stands for; the first letter of a number is not zero
    leading = {FIRST[0], SECOND[0], TOTAL[0]}
    digit = {letter: Integer(letter, 1 if letter in leading else 0, 9, vpool=pool) for letter in letters}
    # carry[k] is what column k passes on to column k + 1, 0 or 1
    carry = [Integer(f"carry_{k}", 0, 1, vpool=pool) for k in range(width - 1)]
    engine = IntegerEngine(vars=list(digit.values()) + carry, vpool=pool)

    # every letter stands for a different digit
    engine.add_alldifferent(list(digit.values()))

    # The addition is done column by column, from the units up.
    for k in range(width):
        # the two digits of column k plus the carry coming in = the digit of the total
        # plus 10 * the carry going out
        left = digit[FIRST[-1 - k]] + digit[SECOND[-1 - k]]
        if k > 0:
            left = left + carry[k - 1]
        right = digit[TOTAL[-1 - k]]
        if k < width - 1:
            right = right + 10 * carry[k]
        engine.add_linear(left == right)

    return engine.clausify(), {letter: digit[letter] for letter in letters}
