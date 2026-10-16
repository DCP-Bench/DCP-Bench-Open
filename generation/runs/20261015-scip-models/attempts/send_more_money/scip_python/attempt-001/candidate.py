# SEND + MORE = MONEY: assign a distinct digit 0-9 to each letter so that the sum holds.
from pyscipopt import Model, quicksum

LETTERS = ["s", "e", "n", "d", "m", "o", "r", "y"]
DIGITS = range(10)


def build(instance):
    m = Model()
    m.hideOutput()

    # each letter takes one digit: one-hot binaries b[l, v], letter value is their weighted sum
    val = {}
    b = {}
    for l in LETTERS:
        val[l] = m.addVar(name=l, vtype="I", lb=0, ub=9)
        for v in DIGITS:
            b[l, v] = m.addVar(name=f"b_{l}_{v}", vtype="B")
        # each letter has exactly one digit
        m.addCons(quicksum(b[l, v] for v in DIGITS) == 1)
        # the letter's value is the digit it selects
        m.addCons(val[l] == quicksum(v * b[l, v] for v in DIGITS))

    # the digits of different letters are all different
    # each digit is used by at most one letter
    for v in DIGITS:
        m.addCons(quicksum(b[l, v] for l in LETTERS) <= 1)

    # the first letter of each word cannot be zero
    # s leads SEND and m leads MORE
    m.addCons(b["s", 0] == 0)
    m.addCons(b["m", 0] == 0)

    # the sum SEND + MORE = MONEY, column by column in one linear equation
    # SEND + MORE = MONEY: 1000(s+m) + 100(e+o) + 10(n+r) + (d+e) = 10000m + 1000o + 100n + 10e + y
    m.addCons(
        1000 * val["s"] + 100 * val["e"] + 10 * val["n"] + val["d"]
        + 1000 * val["m"] + 100 * val["o"] + 10 * val["r"] + val["e"]
        == 10000 * val["m"] + 1000 * val["o"] + 100 * val["n"] + 10 * val["e"] + val["y"]
    )

    # the output gives the value of each letter
    outputs = {l: val[l] for l in ["d", "e", "m", "n", "o", "r", "s", "y"]}
    return m, outputs
