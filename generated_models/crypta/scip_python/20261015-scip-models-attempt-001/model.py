# Cryptarithmetic puzzle: A_WORD + B_WORD = S_WORD, each letter is one distinct digit 0-9,
# and the first letter of each of the three numbers is not zero.
from pyscipopt import Model, quicksum

# the three numbers as written in the problem statement (the puzzle is fixed; the instance has no fields)
A_WORD = "BAIJJAJIIAHFCFEBBJEA"
B_WORD = "DHFGABCDIDBIFFAGFEJE"
S_WORD = "GJEGACDDHFAFJBFIHEEF"


def build(instance):
    m = Model()
    letters = sorted(set(A_WORD + B_WORD + S_WORD))
    digits = range(10)
    n = len(A_WORD)

    # x[l, v] = 1 if letter l stands for digit v
    x = {(l, v): m.addVar(name=f"x_{l}_{v}", vtype="B") for l in letters for v in digits}
    # the value of each letter
    val = {l: quicksum(v * x[l, v] for v in digits) for l in letters}

    # each letter stands for exactly one digit
    for l in letters:
        m.addCons(quicksum(x[l, v] for v in digits) == 1)
    # each digit is used by exactly one letter
    for v in digits:
        m.addCons(quicksum(x[l, v] for l in letters) == 1)

    # the first letter of each number cannot be zero
    for w in (A_WORD, B_WORD, S_WORD):
        m.addCons(val[w[0]] >= 1)

    # carry[k] = 1 if column k (counted from the right) carries into column k+1
    carry = [m.addVar(name=f"carry_{k}", vtype="B") for k in range(n)]
    # no carry out of the leftmost column, since the sum has the same number of digits
    m.addCons(carry[n - 1] == 0)

    # column addition, from the rightmost digit to the leftmost
    for k in range(n):
        a = A_WORD[n - 1 - k]
        b = B_WORD[n - 1 - k]
        s = S_WORD[n - 1 - k]
        # the digits of this column plus the carry in equal the sum digit plus 10 times the carry out
        if k == 0:
            # the rightmost column has no carry in
            m.addCons(val[a] + val[b] == val[s] + 10 * carry[k])
        else:
            m.addCons(val[a] + val[b] + carry[k - 1] == val[s] + 10 * carry[k])

    outputs = {l: val[l] for l in "ABCDEFGHIJ"}
    return m, outputs
