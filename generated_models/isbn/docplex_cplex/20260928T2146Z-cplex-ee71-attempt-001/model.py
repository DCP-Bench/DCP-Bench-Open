"""ISBN-13: fill in the unknown digits so that the number starts with 978 or 979 and its check digit is right."""
from docplex.mp.model import Model

# An ISBN-13 has 13 digits; the first 12 are weighted 1, 3, 1, 3, ...
LENGTH = 13
WEIGHTS = [1 if i % 2 == 0 else 3 for i in range(LENGTH - 1)]


def build(instance):
    known = instance["isbn_init"]  # a digit, or -1 where it is unknown

    model = Model("isbn")

    # isbn[i] is the i-th digit.
    isbn = model.integer_var_list(LENGTH, 0, 9, name="isbn")

    # The known digits keep their values.
    for i in range(LENGTH):
        if known[i] != -1:
            model.add_constraint(isbn[i] == known[i], ctname=f"known_{i}")

    # The number starts with 978 or 979.
    model.add_constraint(isbn[0] == 9, ctname="prefix0")
    model.add_constraint(isbn[1] == 7, ctname="prefix1")
    model.add_constraint(isbn[2] >= 8, ctname="prefix2")

    # The check digit is (10 - (sum % 10)) % 10 of the weighted sum of the first
    # 12 digits. Because it is a single digit, that is the same as saying the
    # weighted sum plus the check digit is a multiple of 10, which is linear.
    tens = model.integer_var(0, (9 * sum(WEIGHTS) + 9) // 10, name="tens")
    model.add_constraint(model.dot(isbn[:LENGTH - 1], WEIGHTS) + isbn[LENGTH - 1] == 10 * tens,
                         ctname="check_digit")

    return model, {"isbn": isbn}
