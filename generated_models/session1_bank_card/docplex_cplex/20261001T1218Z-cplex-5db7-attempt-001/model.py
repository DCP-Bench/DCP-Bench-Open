"""Bank card PIN abcd: four different digits where cd is three times ab and da is twice bc."""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data.
    letters = "abcd"
    digits = range(10)

    model = Model("bank_card")

    # is_digit[c, v] is 1 when PIN digit c is v; no two digits are the same.
    is_digit = {(c, v): model.binary_var(name=f"{c}_is_{v}") for c in letters for v in digits}
    for c in letters:
        model.add_constraint(model.sum(is_digit[c, v] for v in digits) == 1)
    for v in digits:
        model.add_constraint(model.sum(is_digit[c, v] for c in letters) <= 1)
    value = {c: model.integer_var(0, 9, name=c) for c in letters}
    for c in letters:
        model.add_constraint(value[c] == model.sum(v * is_digit[c, v] for v in digits))
    a, b, c, d = (value[x] for x in letters)

    # The two-digit number cd is 3 times the two-digit number ab.
    model.add_constraint(10 * c + d == 3 * (10 * a + b))
    # The two-digit number da is 2 times the two-digit number bc.
    model.add_constraint(10 * d + a == 2 * (10 * b + c))

    return model, dict(value)
