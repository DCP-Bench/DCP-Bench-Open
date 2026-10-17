# Send More Money (cryptarithmetic puzzle) in cvc5 (pythonic API).
# Assign a unique digit 0-9 to each letter s, e, n, d, m, o, r, y so that
#    SEND + MORE = MONEY
# holds as integers, and the first letter of each word is not zero.
import cvc5.pythonic as cz


def build(instance):
    s, e, n, d, m, o, r, y = cz.Ints("s e n d m o r y")
    letters = [s, e, n, d, m, o, r, y]

    constraints = []

    # Each letter represents a digit from 0 to 9.
    # Each letter must be assigned a unique digit from 0 to 9.
    for v in letters:
        constraints.append(v >= 0)
        constraints.append(v <= 9)
    constraints.append(cz.Distinct(letters))

    # The first letter of each word cannot be zero.
    constraints.append(s != 0)
    constraints.append(m != 0)

    # The goal is to assign digits to the letters such that the equation
    # SEND + MORE = MONEY holds true.
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m + 100 * o + 10 * r + e
    money = 10000 * m + 1000 * o + 100 * n + 10 * e + y
    constraints.append(send + more == money)

    outputs = {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}
    return constraints, outputs
