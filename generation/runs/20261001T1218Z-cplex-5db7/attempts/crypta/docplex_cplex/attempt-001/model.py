"""Crypta (Van Hentenryck): the cryptarithmetic sum
BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF
where every letter is a distinct digit and no number starts with zero.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the letters and the sum are fixed by the statement.
    letters = "ABCDEFGHIJ"
    digits = range(10)

    model = Model("crypta")

    # is_digit[c, d] is 1 when letter c stands for digit d; each letter is one digit and the
    # letters are all different digits.
    is_digit = {(c, d): model.binary_var(name=f"{c}_is_{d}") for c in letters for d in digits}
    for c in letters:
        model.add_constraint(model.sum(is_digit[c, d] for d in digits) == 1)
    for d in digits:
        model.add_constraint(model.sum(is_digit[c, d] for c in letters) <= 1)

    value = {c: model.integer_var(0, 9, name=c) for c in letters}
    for c in letters:
        model.add_constraint(value[c] == model.sum(d * is_digit[c, d] for d in digits))
    A, B, C, D, E, F, G, H, I, J = (value[c] for c in letters)

    # The first letter of each number is not zero.
    model.add_constraint(B >= 1)
    model.add_constraint(D >= 1)
    model.add_constraint(G >= 1)

    # The sum is split into three column blocks of 7, 7 and 6 digits, with carries Sr1 and
    # Sr2 from one block into the next, as in the reference.
    Sr1 = model.binary_var(name="Sr1")
    Sr2 = model.binary_var(name="Sr2")

    # Lowest seven columns.
    model.add_constraint(
        A + 10 * E + 100 * J + 1000 * B + 10000 * B + 100000 * E + 1000000 * F
        + E + 10 * J + 100 * E + 1000 * F + 10000 * G + 100000 * A + 1000000 * F
        == F + 10 * E + 100 * E + 1000 * H + 10000 * I + 100000 * F + 1000000 * B
        + 10000000 * Sr1)
    # Middle seven columns, with the carry Sr1 coming in.
    model.add_constraint(
        C + 10 * F + 100 * H + 1000 * A + 10000 * I + 100000 * I + 1000000 * J
        + F + 10 * I + 100 * B + 1000 * D + 10000 * I + 100000 * D + 1000000 * C + Sr1
        == J + 10 * F + 100 * A + 1000 * F + 10000 * H + 100000 * D + 1000000 * D
        + 10000000 * Sr2)
    # Highest six columns, with the carry Sr2 coming in.
    model.add_constraint(
        A + 10 * J + 100 * J + 1000 * I + 10000 * A + 100000 * B
        + B + 10 * A + 100 * G + 1000 * F + 10000 * H + 100000 * D + Sr2
        == C + 10 * A + 100 * G + 1000 * E + 10000 * J + 100000 * G)

    return model, dict(value)
