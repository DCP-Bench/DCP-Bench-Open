# A Dudeney number is a positive integer that is a perfect cube such that the sum of
# its digits is equal to the cube root of the number. Find one (number) larger than 1.
# The instance field n is the maximum number of digits.
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    cons = []

    # the number has at most n digits: digit position p (0 = units) holds exactly one digit
    d = [[Bool(f"d_{p}_{v}") for v in range(10)] for p in range(n)]
    for p in range(n):
        cons.append(sum(d[p]) == 1)

    # the cube root r, one-hot; r >= 2 makes the number larger than 1.
    # Its digit sum is at most 9n, so r is at most 9n.
    r_max = 9 * n
    roots = {r: Bool(f"r_{r}") for r in range(2, r_max + 1)}
    cons.append(sum(roots.values()) == 1)

    digit_value = [sum(v * d[p][v] for v in range(10)) for p in range(n)]

    # the number is a perfect cube: its value is r^3 for the chosen root
    number = sum(10 ** p * digit_value[p] for p in range(n))
    cons.append(number == sum(r ** 3 * b for r, b in roots.items()))

    # the sum of its digits is equal to the cube root of the number
    digit_sum = sum(digit_value)
    cons.append(digit_sum == sum(r * b for r, b in roots.items()))

    return cons, {"number": number}
