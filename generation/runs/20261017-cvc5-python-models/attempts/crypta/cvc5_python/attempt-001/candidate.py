# Cryptarithmetic puzzle "crypta": solve the addition of the three words below,
# where each letter is a digit. The words are written one letter per digit and
# right-aligned, so the addition is checked column by column with carries.
import cvc5.pythonic as cz

ADDEND_1 = "BAIJJAJIIAHFCFEBBJEA"
ADDEND_2 = "DHFGABCDIDBIFFAGFEJE"
SUM = "GJEGACDDHFAFJBFIHEEF"
LETTERS = "ABCDEFGHIJ"


def build(instance):
    d = {c: cz.Int(f"d_{c}") for c in LETTERS}
    constraints = []

    # all letters are distinct digits from 0 to 9
    for c in LETTERS:
        constraints.append(d[c] >= 0)
        constraints.append(d[c] <= 9)
    constraints.append(cz.Distinct(list(d.values())))

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
