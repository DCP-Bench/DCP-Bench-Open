# Problem session5_hardy_1729_square: find four different numbers between 1 and 100
# such that the sum of the squares of the two first numbers equals the sum of the
# squares of the other two numbers, a^2 + b^2 = c^2 + d^2.
# Output the numbers (a, b, c, d).

import cvc5.pythonic as cz


def build(instance):
    a, b, c, d = cz.Ints("a b c d")

    # The numbers lie in 1..100 (fixed by the description, not by the data).
    bounds = [cz.And(v >= 1, v <= 100) for v in (a, b, c, d)]

    # Four different numbers.
    different = [cz.Distinct([a, b, c, d])]

    # The sum of the squares of the two first numbers equals the sum of the squares
    # of the other two.
    same_square_sum = [a * a + b * b == c * c + d * d]

    return bounds + different + same_square_sum, {"a": a, "b": b, "c": c, "d": d}
