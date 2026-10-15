# My bank card has a 4 digit pin, abcd: a, b, c, d are the four digits of the PIN.
# Each digit is one-hot over the values 0..9.
from paramita.modelling import Bool

POSITIONS = ["a", "b", "c", "d"]
DIGITS = range(10)


def build(instance):
    # one-hot: x[P][v] is true when digit P of the PIN equals v
    x = {P: {v: Bool(f"x_{P}_{v}") for v in DIGITS} for P in POSITIONS}
    cons = []

    # each digit of the PIN is exactly one value
    for P in POSITIONS:
        cons.append(sum(x[P][v] for v in DIGITS) == 1)

    # no two digits are the same: every value is used by at most one position
    for v in DIGITS:
        cons.append(sum(x[P][v] for P in POSITIONS) <= 1)

    val = {P: sum(v * x[P][v] for v in DIGITS) for P in POSITIONS}
    a, b, c, d = val["a"], val["b"], val["c"], val["d"]

    # the 2-digit number cd is 3 times the 2-digit number ab
    cons.append(10 * c + d == 3 * (10 * a + b))

    # the 2-digit number da is 2 times the 2-digit number bc
    cons.append(10 * d + a == 2 * (10 * b + c))

    outputs = {"a": a, "b": b, "c": c, "d": d}
    return cons, outputs
