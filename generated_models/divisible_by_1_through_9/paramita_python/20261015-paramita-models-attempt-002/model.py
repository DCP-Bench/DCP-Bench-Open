# Problem: find a 10 digit number that uses each of the digits 0 to 9 exactly once,
# where the number formed by the first n digits is divisible by n (n = 1..10).
# Digits are read from left to right; position p = 1..10 is the p-th digit.
# Integer encoding: each digit is one-hot over the values 0..9.
# The instance carries no fields for this problem, so build() takes no data from it.
from paramita.modelling import Bool

POSITIONS = range(1, 11)
DIGITS = range(10)


def build(instance):
    # y[p][v] is true when digit v is at position p (one-hot digit).
    y = {p: {v: Bool(f"digit_{p}_is_{v}") for v in DIGITS} for p in POSITIONS}
    cons = []

    # a 10 digit number: every position holds exactly one digit
    cons += [sum(y[p].values()) == 1 for p in POSITIONS]
    # a 10 digit number: the leading digit is not zero
    cons.append(~y[1][0])

    # uses each of the digits 0 to 9 exactly once: each digit is placed in exactly one position
    cons += [sum(y[p][v] for p in POSITIONS) == 1 for v in DIGITS]

    # value of the digit at position p, as an integer expression over the one-hot Bools
    digit = {p: sum(v * y[p][v] for v in DIGITS) for p in POSITIONS}

    # the number formed by the first n digits is divisible by n, for n = 2..10
    # (n = 1 is trivially true for any digit).
    # The prefix value is sum_{p<=n} 10^(n-p) d_p. Each weight is replaced by its
    # residue mod n, which keeps the sum congruent mod n and keeps the weights small.
    for n in range(2, 11):
        residue = {p: pow(10, n - p, n) for p in range(1, n + 1)}
        # largest possible residue-weighted sum, bounding the quotient t
        max_sum = sum(9 * residue[p] for p in range(1, n + 1))
        top = max_sum // n
        # quotient t of the prefix sum by n, one-hot over 0..top
        t = {j: Bool(f"prefix_{n}_quotient_is_{j}") for j in range(top + 1)}
        cons.append(sum(t.values()) == 1)
        # the residue-weighted prefix sum equals n times its quotient
        cons.append(
            sum(residue[p] * digit[p] for p in range(1, n + 1))
            == sum(n * j * t[j] for j in range(1, top + 1))
        )

    # print the number: its ten digits read from left to right
    number = sum(10 ** (10 - p) * digit[p] for p in POSITIONS)
    return cons, {"number": number}
