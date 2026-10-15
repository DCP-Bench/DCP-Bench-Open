"""General store (cryptarithmetic puzzle).

The owner's sum: sixteen words added column by column give ALL WOOL.
Each letter stands for a different digit (0-9). The statement sets no rule on leading zeros.
The problem has no instance data: the words below are the statement's own puzzle.
"""

from paramita.modelling import Bool, If

# The addends above the line, in the order of the statement.
ADDENDS = [
    "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
    "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
]
TOTAL = "ALLWOOL"
DIGITS = range(10)
COLUMNS = len(TOTAL)  # 7 columns, rightmost is column 0


def build(instance):
    words = ADDENDS + [TOTAL]
    letters = sorted({ch for w in words for ch in w})  # the ten letters of the puzzle

    # each different letter stands for a different digit: x[L][d] = 1 if letter L stands for digit d
    x = {L: {d: Bool(f"x_{L}_{d}") for d in DIGITS} for L in letters}

    def value(L):
        """The digit of letter L as an integer expression."""
        return sum(d * x[L][d] for d in DIGITS)

    cons = []

    # each letter stands for exactly one digit
    cons += [sum(x[L].values()) == 1 for L in letters]

    # each different letter stands for a different digit (ten letters, ten digits)
    cons += [sum(x[L][d] for L in letters) == 1 for d in DIGITS]

    # carries: carry[j] is the carry into column j, carry[0] = 0, and the sum has no digit beyond column 6, so carry[7] = 0
    carry = {0: 0, COLUMNS: 0}
    # bound on each carry (a derived bound, not from the statement): the digits of the
    # column plus the carry in, divided by ten; it keeps the unary carry bits short
    bound = {0: 0}
    for j in range(COLUMNS):
        n_j = sum(1 for w in ADDENDS if len(w) > j)
        bound[j + 1] = (9 * n_j + bound[j]) // 10
    for j in range(1, COLUMNS):
        # carry[j] as unary bits: bits[i] means carry[j] >= i + 1
        size = bound[j]
        bits = [Bool(f"carry_{j}_ge_{i}") for i in range(1, size + 1)]
        for i in range(size - 1):
            cons.append(If(bits[i + 1], bits[i]))
        carry[j] = sum(bits)

    # the sixteen words add up to ALL WOOL, column by column from the right
    for j in range(COLUMNS):
        # the letters of the addends in column j (from the right), plus the carry in
        column_addends = [value(w[-1 - j]) for w in ADDENDS if len(w) > j]
        left = sum(column_addends) + carry[j]
        # equals the letter of ALL WOOL in column j, plus ten times the carry out
        right = value(TOTAL[-1 - j]) + 10 * carry[j + 1]
        cons.append(left == right)

    outputs = {L: value(L) for L in letters}
    return cons, outputs
