# Cryptarithm: solve BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF, where
# the letters are distinct digits and no number starts with zero.
from pychoco.model import Model

# The puzzle has no instance data; the three words are its statement.
LETTERS = "ABCDEFGHIJ"
TERM1 = "BAIJJAJIIAHFCFEBBJEA"
TERM2 = "DHFGABCDIDBIFFAGFEJE"
TOTAL = "GJEGACDDHFAFJBFIHEEF"


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # digit[L] = the digit of letter L
    digit = {L: model.intvar(0, 9, name=L) for L in LETTERS}

    # All letters are distinct digits.
    model.all_different(list(digit.values())).post()

    # The first letter of each number is not zero.
    for word in (TERM1, TERM2, TOTAL):
        model.arithm(digit[word[0]], ">=", 1).post()

    # Column-by-column addition, from the units column up. carry[c] is the carry into column c
    # (counted from the right); nothing carries into the units column and nothing carries out of
    # the leftmost column, since the sum has as many digits as the terms. This states the same
    # sum as the reference's three blocks of digits joined by two carries.
    width = len(TOTAL)
    carry = [model.intvar(0, 1, name=f"carry_{c}") for c in range(width + 1)]
    model.arithm(carry[0], "=", 0).post()
    model.arithm(carry[width], "=", 0).post()
    for c in range(width):
        pos = width - 1 - c  # string position of column c
        model.scalar(
            [digit[TERM1[pos]], digit[TERM2[pos]], carry[c], digit[TOTAL[pos]], carry[c + 1]],
            [1, 1, 1, -1, -10], "=", 0).post()

    return model, digit
