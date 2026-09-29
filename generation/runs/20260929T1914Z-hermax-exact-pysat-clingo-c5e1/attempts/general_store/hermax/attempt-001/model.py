# General store: each letter of the sign stands for a different digit, and the
# sixteen words above the line add up to ALL WOOL.
from hermax.model import Model

WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
         "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    letters = sorted(set("".join(WORDS) + TOTAL))
    width = len(TOTAL)

    m = Model()
    # digit[letter] = the digit the letter stands for
    digit = {letter: m.int(letter, 0, 9) for letter in letters}
    # every letter stands for a different digit
    m &= m.vector([digit[letter] for letter in letters]).all_different()

    # The addition is done column by column, from the units up. carry[k] is what
    # column k passes on to column k + 1; at most 15 as the column adds 16 digits.
    carry = [m.int(f"carry_{k}", 0, 15) for k in range(width - 1)]
    for k in range(width):
        column = [word[-1 - k] for word in WORDS if len(word) > k]
        total_letter = TOTAL[-1 - k]
        # digits of column k plus the carry coming in = digit of the total plus 10 * carry going out
        left = sum(digit[letter] for letter in column)
        if k > 0:
            left = left + carry[k - 1]
        right = digit[total_letter]
        if k < width - 1:
            right = right + 10 * carry[k]
        m &= (left == right)

    return m, {letter: digit[letter] for letter in letters}
