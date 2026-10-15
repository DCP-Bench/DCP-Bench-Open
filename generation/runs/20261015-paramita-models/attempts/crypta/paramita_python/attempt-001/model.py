# Cryptarithmetic puzzle: solve the addition
#   B A I J J A J I I A H F C F E B B J E A
# + D H F G A B C D I D B I F F A G F E J E
# = G J E G A C D D H F A F J B F I H E E F
# where all letters are distinct digits from 0 to 9, and the first letter of
# each number cannot be zero. Output: the digit of each letter A..J.
#
# The puzzle is fixed by the problem statement, so the model does not read the
# instance argument.

from paramita.modelling import Bool

# The three numbers, letter by letter, from the most significant position.
FIRST = "BAIJJAJIIAHFCFEBBJEA"
SECOND = "DHFGABCDIDBIFFAGFEJE"
RESULT = "GJEGACDDHFAFJBFIHEEF"
LETTERS = "ABCDEFGHIJ"
# First letter of each of the three numbers.
LEADING = ("B", "D", "G")
DIGITS = range(10)


def build(instance):
    # each letter is one digit: one-hot Bools, exactly one value per letter
    x = {L: [Bool(f"x_{L}_{v}") for v in DIGITS] for L in LETTERS}
    cons = [sum(x[L]) == 1 for L in LETTERS]

    # the value of a letter, as an integer expression over its one-hot Bools
    val = {L: sum(v * x[L][v] for v in range(1, 10)) for L in LETTERS}

    # all letters are distinct: every digit is used by exactly one letter
    cons += [sum(x[L][v] for L in LETTERS) == 1 for v in DIGITS]

    # the first letter of each number cannot be zero
    cons += [~x[L][0] for L in LEADING]

    # carry[k] is the carry out of column k, counted from the right (column 0 is the last digit)
    carry = [Bool(f"carry_{k}") for k in range(len(RESULT))]
    # the sum has no digit beyond the last column, so the top carry is zero
    cons.append(~carry[len(RESULT) - 1])

    # column by column: digit of the first number + digit of the second number
    # + carry from the column to the right = digit of the result + 10 * carry out
    for k in range(len(RESULT)):
        i = len(RESULT) - 1 - k
        a, b, r = val[FIRST[i]], val[SECOND[i]], val[RESULT[i]]
        if k == 0:
            cons.append(a + b == r + 10 * carry[k])
        else:
            cons.append(a + b + carry[k - 1] == r + 10 * carry[k])

    outputs = {L: val[L] for L in LETTERS}
    return cons, outputs
