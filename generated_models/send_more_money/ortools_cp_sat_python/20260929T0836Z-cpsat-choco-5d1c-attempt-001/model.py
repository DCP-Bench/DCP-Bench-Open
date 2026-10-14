# SEND + MORE = MONEY: give each letter a different digit, with no leading zero
# in SEND, MORE or MONEY, so that the addition is correct.
from ortools.sat.python import cp_model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    model = cp_model.CpModel()

    s, e, n, d, m, o, r, y = letters = [model.new_int_var(0, 9, name) for name in "sendmory"]

    # every letter stands for a different digit
    model.add_all_different(letters)

    # no word starts with zero: SEND starts with S, MORE and MONEY with M
    model.add(s > 0)
    model.add(m > 0)

    # SEND + MORE = MONEY, each word read as a number
    model.add(
        1000 * s + 100 * e + 10 * n + d + 1000 * m + 100 * o + 10 * r + e
        == 10000 * m + 1000 * o + 100 * n + 10 * e + y
    )

    return model, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}
