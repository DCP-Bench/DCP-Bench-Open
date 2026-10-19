# Cryptarithmetic puzzle "crypta": solve the addition of the three words below,
# where each letter is a digit. The words are written one letter per digit and
# right-aligned, so the addition is checked column by column with carries.
# Each letter takes one digit (one-hot Booleans), and each digit goes to one letter.
import cvc5.pythonic as cz

ADDEND_1 = "BAIJJAJIIAHFCFEBBJEA"
ADDEND_2 = "DHFGABCDIDBIFFAGFEJE"
SUM = "GJEGACDDHFAFJBFIHEEF"
LETTERS = "ABCDEFGHIJ"
DIGITS = range(10)


def build(instance):
    constraints = []

    # where all letters are distinct digits from 0 to 9
    pick = {c: [cz.Bool(f"p_{c}_{v}") for v in DIGITS] for c in LETTERS}
    d = {}
    for c in LETTERS:
        constraints.append(cz.Or([pick[c][v] for v in DIGITS]))
        for v1 in DIGITS:
            for v2 in DIGITS:
                if v1 < v2:
                    constraints.append(cz.Or(cz.Not(pick[c][v1]), cz.Not(pick[c][v2])))
        d[c] = cz.Sum([cz.If(pick[c][v], v, 0) for v in DIGITS])
    for v in DIGITS:
        holders = [pick[c][v] for c in LETTERS]
        # each digit is used by at most one letter
        for i in range(len(holders)):
            for j in range(i + 1, len(holders)):
                constraints.append(cz.Or(cz.Not(holders[i]), cz.Not(holders[j])))

    # the first letter of each number cannot be zero
    for word in (ADDEND_1, ADDEND_2, SUM):
        constraints.append(d[word[0]] != 0)

    # the addition, column by column, with the carry from the column on the right
    n = len(SUM)
    carry = [cz.Int(f"carry_{i}") for i in range(n + 1)]
    constraints += [carry[0] == 0, carry[n] == 0]
    for i in range(1, n):
        constraints += [carry[i] >= 0, carry[i] <= 1]
    for i in range(n):
        a = d[ADDEND_1[i]]
        b = d[ADDEND_2[i]]
        s = d[SUM[i]]
        constraints.append(a + b + carry[i + 1] == s + 10 * carry[i])

    outputs = {c: d[c] for c in LETTERS}
    return constraints, outputs
