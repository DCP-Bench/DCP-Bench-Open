# SEND + MORE = MONEY: give each letter a different digit, with no leading zero
# in SEND, MORE or MONEY, so that the addition is correct.
from hermax.model import Model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    m = Model()
    letters = {name: m.int(name, 0, 9) for name in "sendmory"}
    s, e, n, d, mm, o, r, y = (letters[name] for name in "sendmory")

    # every letter stands for a different digit
    m &= m.vector(list(letters.values())).all_different()

    # no word starts with zero: SEND starts with S, MORE and MONEY with M
    m &= (s != 0)
    m &= (mm != 0)

    # SEND + MORE = MONEY, each word read as a number
    m &= (1000 * s + 100 * e + 10 * n + d + 1000 * mm + 100 * o + 10 * r + e
          == 10000 * mm + 1000 * o + 100 * n + 10 * e + y)

    return m, {"s": s, "e": e, "n": n, "d": d, "m": mm, "o": o, "r": r, "y": y}
