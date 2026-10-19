# Dudeney numbers, cvc5 (Python) model.
# A Dudeney number is a positive integer that is a perfect cube such that the sum
# of its digits is equal to the cube root of the number. Print such a number
# (number) that is also larger than 1.
# The instance field n is the digit bound: the number has at most n digits.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    limit = 10 ** n

    # The largest cube root whose cube has at most n digits.
    top = 1
    while (top + 1) ** 3 < limit:
        top += 1

    # A number with at most n digits: n decimal digits, each 0..9.
    digits = [cz.Int(f"d{i}") for i in range(n)]
    number = cz.Int("number")
    root = cz.Int("root")

    constraints = []
    # Digits of the number, each between 0 and 9.
    for d in digits:
        constraints.append(d >= 0)
        constraints.append(d <= 9)

    # The number is the value of its digits.
    constraints.append(number == cz.Sum([d * 10 ** i for i, d in enumerate(digits)]))

    # The number is larger than 1.
    constraints.append(number > 1)

    # The sum of its digits is equal to the cube root of the number.
    constraints.append(cz.Sum(digits) == root)

    # The number is a perfect cube of the root: the root is an integer from 2 up to the
    # largest root whose cube fits in n digits, and the number is its cube.
    cube_options = [cz.And(root == c, number == c ** 3) for c in range(2, top + 1)]
    if len(cube_options) == 1:
        constraints.append(cube_options[0])
    else:
        constraints.append(cz.Or(cube_options))

    return constraints, {"number": number}
