"""SEND + MORE = MONEY: give each letter a different digit so the sum holds, with no word
starting with zero.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data.
    letters = "sendmory"
    digits = range(10)

    model = Model("send_more_money")

    # is_digit[c, d] is 1 when letter c stands for digit d; each letter is one digit and
    # the letters are all different.
    is_digit = {(c, d): model.binary_var(name=f"{c}_is_{d}") for c in letters for d in digits}
    for c in letters:
        model.add_constraint(model.sum(is_digit[c, d] for d in digits) == 1)
    for d in digits:
        model.add_constraint(model.sum(is_digit[c, d] for c in letters) <= 1)
    value = {c: model.integer_var(0, 9, name=c) for c in letters}
    for c in letters:
        model.add_constraint(value[c] == model.sum(d * is_digit[c, d] for d in digits))
    s, e, n, d, m, o, r, y = (value[c] for c in letters)

    # SEND + MORE = MONEY.
    model.add_constraint(1000 * s + 100 * e + 10 * n + d
                         + 1000 * m + 100 * o + 10 * r + e
                         == 10000 * m + 1000 * o + 100 * n + 10 * e + y)
    # S and M lead their words, so they are not zero.
    model.add_constraint(s >= 1)
    model.add_constraint(m >= 1)

    return model, dict(value)
