# SEND + MORE = MONEY: give each letter a different digit so that the sum SEND + MORE = MONEY holds
# and the leading letters S and M are not zero.
import cpmpy as cp


def build(instance):
    # The puzzle has no instance data; the words are the problem statement itself.
    s, e, n, d, m, o, r, y = cp.intvar(0, 9, shape=8)

    model = cp.Model()

    # Different letters take different digits.
    model += cp.AllDifferent([s, e, n, d, m, o, r, y])

    # The first letter of a word cannot be zero.
    model += s > 0
    model += m > 0

    # SEND + MORE = MONEY, each word read as a decimal number.
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m + 100 * o + 10 * r + e
    money = 10000 * m + 1000 * o + 100 * n + 10 * e + y
    model += send + more == money

    return model, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}
