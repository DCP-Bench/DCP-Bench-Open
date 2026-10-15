# SEND + MORE = MONEY: assign a distinct digit 0-9 to each letter s, e, n, d, m, o, r, y.
# Each letter is one-hot over the digits 0..9.
from paramita.modelling import Bool

LETTERS = ["s", "e", "n", "d", "m", "o", "r", "y"]
DIGITS = range(10)


def build(instance):
    # one-hot: x[L][v] is true when letter L takes digit v
    x = {L: {v: Bool(f"x_{L}_{v}") for v in DIGITS} for L in LETTERS}
    cons = []

    # each letter is assigned exactly one digit
    for L in LETTERS:
        cons.append(sum(x[L][v] for v in DIGITS) == 1)

    # each letter must be assigned a unique digit: every digit is used by at most one letter
    for v in DIGITS:
        cons.append(sum(x[L][v] for L in LETTERS) <= 1)

    # the first letter of each word cannot be zero: S and M are not 0
    cons.append(~x["s"][0])
    cons.append(~x["m"][0])

    # SEND + MORE = MONEY, column by column as one linear equation over the digit values
    val = {L: sum(v * x[L][v] for v in DIGITS) for L in LETTERS}
    send = 1000 * val["s"] + 100 * val["e"] + 10 * val["n"] + val["d"]
    more = 1000 * val["m"] + 100 * val["o"] + 10 * val["r"] + val["e"]
    money = 10000 * val["m"] + 1000 * val["o"] + 100 * val["n"] + 10 * val["e"] + val["y"]
    # SEND + MORE = MONEY
    cons.append(send + more == money)

    outputs = {L.lower(): val[L] for L in ["d", "e", "m", "n", "o", "r", "s", "y"]}
    return cons, outputs
