# Problem: curious set of integers. The integers 1, 3, 8 and 120 form a set in which
# the product of any two integers is one less than a perfect square. Find a fifth
# number (larger than or equal to 0) that can be added to the set without destroying
# this property. Print this number (number).
import math

import cvc5.pythonic as cz


def build(instance):
    max_val = instance["max_val"]
    number = cz.Int("number")
    given = [1, 3, 8, 120]

    # The fifth number is at least 0 and at most the bound given by the instance.
    constraints = [number >= 0, number <= max_val]

    # The product of the fifth number with each given integer is one less than a
    # perfect square. The product of two variables is nonlinear, so the square is
    # written as a disjunction over the constant squares j * j up to the largest
    # possible product.
    top = math.isqrt(max(given) * max_val + 1)
    for a in given:
        constraints.append(cz.Or([a * number + 1 == j * j for j in range(top + 1)]))

    return constraints, {"number": number}
