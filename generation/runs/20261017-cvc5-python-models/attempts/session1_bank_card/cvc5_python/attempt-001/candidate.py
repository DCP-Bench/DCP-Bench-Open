# Bank card PIN: a 4-digit PIN abcd, with three facts about its digits.
# Digits a, b, c, d are integers in 0..9 (a PIN is a 4-digit number).
import cvc5.pythonic as cz


def build(instance):
    a, b, c, d = cz.Ints("a b c d")
    digits = [a, b, c, d]
    constraints = []

    # The digits are decimal digits, and the two-digit numbers ab, bc and da
    # must each have a nonzero leading digit.
    constraints += [x >= 0 for x in digits]
    constraints += [x <= 9 for x in digits]
    constraints += [a >= 1, b >= 1, d >= 1]

    # no two digits are the same
    constraints.append(cz.Distinct(digits))

    # the 2-digit number cd is 3 times the 2-digit number ab
    constraints.append(10 * c + d == 3 * (10 * a + b))

    # the 2-digit number da is 2 times the 2-digit number bc
    constraints.append(10 * d + a == 2 * (10 * b + c))

    return constraints, {"a": a, "b": b, "c": c, "d": d}
