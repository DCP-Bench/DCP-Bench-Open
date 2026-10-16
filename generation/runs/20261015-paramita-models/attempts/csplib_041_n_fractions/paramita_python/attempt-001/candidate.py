"""N-fractions puzzle (CSPLib 041), Paramita model.

Find distinct non-zero digits A..I such that
    A / BC + D / EF + G / HI = 1,
where BC = 10*B + C, EF = 10*E + F and HI = 10*H + I are two-digit numbers.
Outputs the nine digits.
"""

from paramita.modelling import Bool, And

DIGITS = "ABCDEFGHI"
VALUES = range(1, 10)  # non-zero digits
BITS = 7  # two-digit numbers are at most 99 < 2**7


def build(instance):
    # d[X][v] = 1 if digit X takes the value v
    d = {X: {v: Bool(f"d_{X}_{v}") for v in VALUES} for X in DIGITS}

    cons = []

    # each digit takes exactly one value
    for X in DIGITS:
        cons.append(sum(d[X].values()) == 1)

    # the nine digits are distinct non-zero digits, so they are a permutation of 1..9:
    # each value is taken by exactly one digit
    for v in VALUES:
        cons.append(sum(d[X][v] for X in DIGITS) == 1)

    def digit_value(X):
        return sum(v * d[X][v] for v in VALUES)

    # the two-digit numbers in binary: BC = 10*B + C, with bits p[i] (weight 2**i)
    def two_digit(tens, units, name):
        bits = [Bool(f"{name}_bit_{i}") for i in range(BITS)]
        cons.append(sum(2**i * bits[i] for i in range(BITS)) == 10 * digit_value(tens) + digit_value(units))
        return bits

    # BC, EF and HI (as bit vectors)
    p = two_digit("B", "C", "p")  # BC = 10*B + C
    q = two_digit("E", "F", "q")  # EF = 10*E + F
    r = two_digit("H", "I", "r")  # HI = 10*H + I

    # products of two bit vectors, one Bool per bit pair
    cache2 = {}

    def and2(x, y):
        key = (x, y)
        if key not in cache2:
            cache2[key] = And([x, y])
        return cache2[key]

    # the cubic equation of the fractions, multiplied by BC*EF*HI:
    #   A*EF*HI + D*BC*HI + G*BC*EF == BC*EF*HI
    # A*EF*HI: the digit A times the product EF*HI, expanded over bit pairs
    terms = []
    for i in range(BITS):
        for j in range(BITS):
            w = 2 ** (i + j)
            for a in VALUES:
                terms.append(a * w * And([d["A"][a], q[i], r[j]]))  # A * EF*HI
            for dv in VALUES:
                terms.append(dv * w * And([d["D"][dv], p[i], r[j]]))  # D * BC*HI
            for gv in VALUES:
                terms.append(gv * w * And([d["G"][gv], p[i], q[j]]))  # G * BC*EF
    lhs = sum(terms)

    # BC*EF*HI: the product of three bit vectors
    rhs = sum(
        2 ** (i + j + k) * And([p[i], q[j], r[k]])
        for i in range(BITS) for j in range(BITS) for k in range(BITS)
    )

    cons.append(lhs == rhs)

    outputs = {X: digit_value(X) for X in DIGITS}
    return cons, outputs
