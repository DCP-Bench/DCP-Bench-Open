# Pythagorean triplet with a + b + c = 1000: find natural numbers a, b, c
# such that a^2 + b^2 = c^2 and a + b + c = 1000, and print a, b, c.
import cvc5.pythonic as cz


def build(instance):
    a, b, c = cz.Ints("a b c")

    # A Pythagorean triplet is a set of three natural numbers a, b, c.
    # Each is at least 1, and the sum fixes an upper bound of 998 on each.
    domain = [a >= 1, a <= 998, b >= 1, b <= 998, c >= 1, c <= 998]

    # There exists exactly one Pythagorean triplet for which a + b + c = 1000.
    sum_rule = [a + b + c == 1000]

    # a^2 + b^2 = c^2
    pythagoras = [a * a + b * b == c * c]

    return domain + sum_rule + pythagoras, {"a": a, "b": b, "c": c}
